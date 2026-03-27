#!/usr/bin/env python3
"""
Configure CloudFront SEO routing:
- rewrite /foo/ -> /foo/index.html
- rewrite /foo  -> /foo/index.html (if no extension)
- keep / unchanged

This allows static SEO folders to work while preserving SPA fallback
via existing CustomErrorResponses (404/403 -> /mapevent.html).
"""

import boto3


DISTRIBUTION_ID = "EMB53HDL7VFIJ"
FUNCTION_NAME = "mapevent-seo-folder-index"
FUNCTION_RUNTIME = "cloudfront-js-1.0"

FUNCTION_CODE = r"""
function handler(event) {
    var request = event.request;
    var uri = request.uri || "/";

    if (uri === "/") {
        return request;
    }

    if (uri.endsWith("/")) {
        request.uri = uri + "index.html";
        return request;
    }

    if (uri.indexOf(".") === -1) {
        request.uri = uri + "/index.html";
    }

    return request;
}
""".strip()


def upsert_function(client):
    functions = client.list_functions()["FunctionList"]
    items = functions.get("Items", [])
    existing = next((f for f in items if f["Name"] == FUNCTION_NAME), None)

    if existing:
        describe = client.describe_function(Name=FUNCTION_NAME)
        etag = describe["ETag"]
        client.update_function(
            Name=FUNCTION_NAME,
            IfMatch=etag,
            FunctionConfig={
                "Comment": "Rewrite folder URLs to index.html for SEO pages",
                "Runtime": FUNCTION_RUNTIME,
            },
            FunctionCode=FUNCTION_CODE.encode("utf-8"),
        )
        new_etag = client.describe_function(Name=FUNCTION_NAME)["ETag"]
        pub = client.publish_function(Name=FUNCTION_NAME, IfMatch=new_etag)
        print(f"[OK] Function updated: {FUNCTION_NAME}")
        return pub["FunctionSummary"]["FunctionMetadata"]["FunctionARN"]

    client.create_function(
        Name=FUNCTION_NAME,
        FunctionConfig={
            "Comment": "Rewrite folder URLs to index.html for SEO pages",
            "Runtime": FUNCTION_RUNTIME,
        },
        FunctionCode=FUNCTION_CODE.encode("utf-8"),
    )
    etag = client.describe_function(Name=FUNCTION_NAME)["ETag"]
    pub = client.publish_function(Name=FUNCTION_NAME, IfMatch=etag)
    print(f"[OK] Function created: {FUNCTION_NAME}")
    return pub["FunctionSummary"]["FunctionMetadata"]["FunctionARN"]


def attach_function_to_distribution(client, function_arn):
    dist = client.get_distribution_config(Id=DISTRIBUTION_ID)
    etag = dist["ETag"]
    config = dist["DistributionConfig"]

    assoc = config["DefaultCacheBehavior"].get("FunctionAssociations", {"Quantity": 0})
    items = assoc.get("Items", [])

    # Remove existing viewer-request association(s), keep others.
    items = [i for i in items if i.get("EventType") != "viewer-request"]
    items.append({"EventType": "viewer-request", "FunctionARN": function_arn})

    config["DefaultCacheBehavior"]["FunctionAssociations"] = {
        "Quantity": len(items),
        "Items": items,
    }

    client.update_distribution(
        Id=DISTRIBUTION_ID,
        IfMatch=etag,
        DistributionConfig=config,
    )
    print("[OK] Function associated to default behavior (viewer-request)")


def main():
    client = boto3.client("cloudfront", region_name="us-east-1")
    function_arn = upsert_function(client)
    attach_function_to_distribution(client, function_arn)
    print("[DONE] CloudFront SEO routing configured")


if __name__ == "__main__":
    main()
