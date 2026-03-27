import boto3

cf = boto3.client("cloudfront", region_name="eu-west-1")

policy_id = "0a16a09f-06c9-4bad-975f-caa6a710939b"
resp = cf.get_response_headers_policy(Id=policy_id)
etag = resp["ETag"]
config = resp["ResponseHeadersPolicy"]["ResponseHeadersPolicyConfig"]

# Remove X-Frame-Options DENY to allow iframe embedding of widgets
# Widgets MUST be embeddable on third-party city/media sites
config["SecurityHeadersConfig"]["FrameOptions"] = {
    "Override": False,
    "FrameOption": "SAMEORIGIN"
}

if not config["SecurityHeadersConfig"]["ContentSecurityPolicy"]:
    del config["SecurityHeadersConfig"]["ContentSecurityPolicy"]

cf.update_response_headers_policy(
    Id=policy_id,
    IfMatch=etag,
    ResponseHeadersPolicyConfig=config,
)
print("Policy mise à jour: X-Frame-Options Override=False (désactivé)")
print("Les widgets peuvent maintenant être intégrés en iframe sur n'importe quel site.")

# Invalidate CloudFront cache
dist_id = "EMB53HDL7VFIJ"
inv = cf.create_invalidation(
    DistributionId=dist_id,
    InvalidationBatch={
        "Paths": {"Quantity": 2, "Items": ["/widget-promo.html", "/villes.html"]},
        "CallerReference": "fix-xframe-" + str(__import__("time").time()),
    },
)
print(f"Cache invalidé: {inv['Invalidation']['Id']}")
