#!/usr/bin/env python3
"""Validate every OpenAPI example in a spec against its own schema.

This catches the checklist-F class of bug that `validateSpec` does not:
an example that contradicts the schema it belongs to.

Usage (from the repo root, or anywhere with an absolute path):

    python3 validate-examples.py apis/paysafe-wallet-saas-chatbot.yaml

Needs `pyyaml` and `jsonschema`. If they are missing:

    python3 -m venv /tmp/.oasvenv && /tmp/.oasvenv/bin/pip -q install pyyaml jsonschema
    /tmp/.oasvenv/bin/python validate-examples.py <spec>

Exit code is 1 when any example fails, so it can gate a loop.
"""

import collections
import os
import re
import sys

try:
    import yaml
    from jsonschema import Draft7Validator
except ImportError:
    sys.exit("missing deps: pip install pyyaml jsonschema (see docstring for a venv one-liner)")

MAX_DEPTH = 60  # guards against a $ref cycle


def main(spec_path):
    spec_path = os.path.abspath(spec_path)
    root = os.path.dirname(spec_path) + os.sep
    main_name = os.path.basename(spec_path)
    raw = open(spec_path).read()
    docs = {}

    def load(name):
        if name not in docs:
            with open(root + name) as handle:
                docs[name] = yaml.safe_load(handle)
        return docs[name]

    def split_ref(ref, curfile):
        """Return (target_node, file_the_target_lives_in) for a $ref string."""
        if ref.startswith("#/"):
            target, path = load(curfile), ref[2:]
        else:
            filename, fragment = ref.split("#")
            curfile = filename.lstrip("./")
            target, path = load(curfile), fragment[1:]
        for part in path.split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        return target, curfile

    def normalise(schema):
        """Translate OpenAPI 3.0 (Draft4-flavoured) keywords into Draft7 equivalents."""
        for bound in ("minimum", "maximum"):
            flag = "exclusive" + bound.capitalize()
            if schema.get(flag) is True and bound in schema:
                schema[flag] = schema.pop(bound)
            elif schema.get(flag) is False:
                schema.pop(flag)
        if schema.pop("nullable", False) and "type" in schema:
            kinds = schema["type"]
            kinds = kinds if isinstance(kinds, list) else [kinds]
            if "null" not in kinds:
                schema["type"] = kinds + ["null"]
        return schema

    def inline(node, curfile, depth=0):
        """Recursively inline $refs so jsonschema can validate against a plain schema."""
        if depth > MAX_DEPTH:
            return {}
        if isinstance(node, list):
            return [inline(i, curfile, depth + 1) for i in node]
        if not isinstance(node, dict):
            return node
        if "$ref" in node:
            target, filename = split_ref(node["$ref"], curfile)
            return inline(target, filename, depth + 1)

        discriminator = node.get("discriminator") or {}
        variants = node.get("oneOf") or node.get("anyOf")
        mapping = discriminator.get("mapping")

        # A discriminator picks exactly one variant. Without it, overlapping variants
        # make `oneOf` report false "valid under each of" errors, so model the
        # discriminator as an if/then chain instead of dropping it.
        if mapping and variants:
            prop = discriminator["propertyName"]
            rest = {k: inline(v, curfile, depth + 1) for k, v in node.items()
                    if k not in ("discriminator", "oneOf", "anyOf", "allOf")}
            branches = list(inline(node.get("allOf", []), curfile, depth + 1))
            for value, ref in mapping.items():
                target, filename = split_ref(ref, curfile)
                branches.append({
                    "if": {"properties": {prop: {"const": value}}, "required": [prop]},
                    "then": inline(target, filename, depth + 1),
                })
            # The value must match one of the declared discriminator values.
            branches.append({"properties": {prop: {"enum": list(mapping)}}})
            rest["allOf"] = branches
            return normalise(rest)

        # `discriminator` without a mapping is only a hint; drop it.
        return normalise({k: inline(v, curfile, depth + 1)
                          for k, v in node.items() if k != "discriminator"})

    def deref(node, curfile):
        """Follow a $ref wrapper on a response / requestBody, keeping track of the file."""
        seen = 0
        while isinstance(node, dict) and "$ref" in node and seen < MAX_DEPTH:
            node, curfile = split_ref(node["$ref"], curfile)
            seen += 1
        return node, curfile

    def line_of(name):
        match = re.search(r"^\s*%s:" % re.escape(name), raw, re.M)
        return raw[: match.start()].count("\n") + 1 if match else 0

    failures = checked = 0

    def check(schema_node, examples, where, curfile):
        nonlocal failures, checked
        if not examples:
            return
        try:
            schema = inline(schema_node, curfile)
        except Exception as exc:  # unresolvable ref: report, do not crash the run
            print("  !! cannot resolve schema at %s: %s" % (where, exc))
            return
        for name, holder in examples.items():
            value = holder.get("value") if isinstance(holder, dict) and "value" in holder else holder
            checked += 1
            errors = sorted(Draft7Validator(schema).iter_errors(value), key=lambda e: list(e.path))
            if errors:
                failures += 1
                print("\nFAIL  %s  example=%s  (~line %d)" % (where, name, line_of(name)))
                for err in errors[:6]:
                    loc = "/".join(str(p) for p in err.path) or "<root>"
                    print("      - %s: %s" % (loc, err.message[:200]))

    spec = load(main_name)
    shared = collections.defaultdict(list)

    for path, operations in (spec.get("paths") or {}).items():
        for verb, op in operations.items():
            if verb not in ("get", "post", "put", "patch", "delete", "head", "options"):
                continue
            oid = op.get("operationId", verb)
            body, filename = deref(op.get("requestBody") or {}, main_name)
            content = (body.get("content") or {}).get("application/json", {})
            if content.get("schema"):
                check(content["schema"], content.get("examples", {}),
                      "%s %s [%s] request" % (verb.upper(), path, oid), filename)
            for code, response in (op.get("responses") or {}).items():
                if isinstance(response, dict) and "$ref" in response:
                    shared[response["$ref"]].append("%s %s" % (oid, code))
                resolved, filename = deref(response, main_name)
                content = (resolved.get("content") or {}).get("application/json", {})
                if content.get("schema"):
                    check(content["schema"], content.get("examples", {}),
                          "%s %s [%s] %s" % (verb.upper(), path, oid, code), filename)

    reused = {k: v for k, v in shared.items() if len(v) > 1}
    if reused:
        # Checklist F: examples on a shared response must make sense for every operation.
        print("\n--- responses shared by more than one operation (check each fits) ---")
        for ref, users in reused.items():
            print("  %-34s %s" % (ref.split("/")[-1], ", ".join(users)))

    print("\n%s\nexamples checked: %d   FAILING: %d" % ("=" * 66, checked, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
