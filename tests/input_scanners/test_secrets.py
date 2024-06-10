import pytest

from llm_guard.input_scanners.secrets import Secrets


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid,expected_score",
    [
        (
            "Just a simple prompt",
            "Just a simple prompt",
            True,
            0.0,
        ),  # Prompt without sensitive data
        (
            'I need to pass a key\naws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"',  # gitleaks:allow
            'I need to pass a key\naws_secret_access_key="************"',
            False,
            1.0,
        ),  # Prompt with key
        (
            "My github token is: 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",  # gitleaks:allow
            "My github token is: ************",
            False,
            1.0,
        ),  # Prompt with Github token
        (
            "My JWT token is: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",  # gitleaks:allow
            "My JWT token is: ******SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            False,
            1.0,
        ),  # Prompt with a JWT token
        (
            "Use this URL: https://username:password@llm-guard.com",
            "Use this URL: https://username:******@llm-guard.com",
            False,
            1.0,
        ),  # Prompt with HTTP basic auth
        (
            '{"awsAccountId":"327878933619","digestStartTime":"2023-10-15T22:04:04Z","digestEndTime":"2023-10-15T23:04:04Z","digestS3Bucket":"llm-guard-trail","digestS3Object":"AWSLogs\/327878933619\/CloudTrail-Digest\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail-Digest_ap-northeast-1_llm-guard-trail_us-west-2_20231015T230404Z.json.gz","digestPublicKeyFingerprint":"be2f0b997552f44942837300ba1aba9d","digestSignatureAlgorithm":"SHA256withRSA","newestEventTime":"2023-10-15T22:58:17Z","oldestEventTime":"2023-10-15T22:04:51Z","previousDigestS3Bucket":"llm-guard-trail","previousDigestS3Object":"AWSLogs\/327878933619\/CloudTrail-Digest\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail-Digest_ap-northeast-1_llm-guard-trail_us-west-2_20231015T220404Z.json.gz","previousDigestHashValue":"8f953371d3e85eddb89b05ed6b9e680791055315c73e1025ab5dba7bb2aee189","previousDigestHashAlgorithm":"SHA-256","previousDigestSignature":"11c11e253f4929eaded49c9d826b257a5ab894ce002988bd07ed2bc6407f1b0ef74f48634c364c6884c6470c9416d73f0742f8758746fc8db4cf23b75c713304779bb6d181ccae4b6a78ae5106f1602ce49af3f9dea4e9ba92761fcaf3e02a5f3d64558d7f4b2eff85f0cc523a770a3b1092e0e37aa665f3c37b75ecc93c94a4640825e0ebe44b2b4fa48b7477040f08a83db2224b403c46476ca25a1b53b5b5db86be04e623fef2d9a2a8eba482239439d6d49cb5eb759a90184f72506a8788fb085f56830c46f51d6e216152bf9156b33cbbee3aeeb5b00540f333708f870d316291f37dd530491a7785ddafdb83543c327fa504e200efefbadd644fed9b9a","logFiles":[{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2205Z_iRIoDMA9l9Q4kmFy.json.gz","hashValue":"4309c6161e37538de72ec6f679e86b7e45aebed71fa7e76af70c3019fef44e19","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:04:51Z","oldestEventTime":"2023-10-15T22:04:51Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2300Z_aDYIgZODwysx0Irn.json.gz","hashValue":"de90c3b55016bc5fad9c12378ccc6fc38180a15bd95879305415572a4472b1a9","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:58:17Z","oldestEventTime":"2023-10-15T22:58:17Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2300Z_9eJ8qdKnXIfFg2wM.json.gz","hashValue":"85e79f9b40d5a57be15fa6ac6f54d3ea1919611e37ca682c1e753287ac7b9bcb","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:58:17Z","oldestEventTime":"2023-10-15T22:58:17Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2225Z_OviGSSWadUI1W1r7.json.gz","hashValue":"58583ed7d52597e47e073db9b756f38815a8a5aff92911911710f18e65e1c44d","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:20:34Z","oldestEventTime":"2023-10-15T22:10:12Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2225Z_j5hj9VuYmchJHAkK.json.gz","hashValue":"c18c49161f97def10a14cffa5b5ab441c8fe8194af1cb1d79d470b6173f901c4","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:20:34Z","oldestEventTime":"2023-10-15T22:20:34Z"}]}',  # gitleaks:allow
            '{"awsAccountId":"327878933619","digestStartTime":"2023-10-15T22:04:04Z","digestEndTime":"2023-10-15T23:04:04Z","digestS3Bucket":"llm-guard-trail","digestS3Object":"AWSLogs\/327878933619\/CloudTrail-Digest\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail-Digest_ap-northeast-1_llm-guard-trail_us-west-2_20231015T230404Z.json.gz","digestPublicKeyFingerprint":"******","digestSignatureAlgorithm":"SHA256withRSA","newestEventTime":"2023-10-15T22:58:17Z","oldestEventTime":"2023-10-15T22:04:51Z","previousDigestS3Bucket":"llm-guard-trail","previousDigestS3Object":"AWSLogs\/327878933619\/CloudTrail-Digest\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail-Digest_ap-northeast-1_llm-guard-trail_us-west-2_20231015T220404Z.json.gz","previousDigestHashValue":"******","previousDigestHashAlgorithm":"SHA-256","previousDigestSignature":"******","logFiles":[{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2205Z_iRIoDMA9l9Q4kmFy.json.gz","hashValue":"4309c6161e37538de72ec6f679e86b7e45aebed71fa7e76af70c3019fef44e19","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:04:51Z","oldestEventTime":"2023-10-15T22:04:51Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2300Z_aDYIgZODwysx0Irn.json.gz","hashValue":"de90c3b55016bc5fad9c12378ccc6fc38180a15bd95879305415572a4472b1a9","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:58:17Z************","logFiles":[{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2205Z_iRIoDMA9l9Q4kmFy.json.gz","hashValue":"4309c6161e37538de72ec6f679e86b7e45aebed71fa7e76af70c3019fef44e19","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:04:51Z","oldestEventTime":"2023-10-15T22:04:51Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/3278789******oudTrail_ap-northeast-1_20231015T2300Z_aDYIgZODwysx0Irn.json.gz","hashValue":"de90c3b55016bc5fad9c12378ccc6fc38180a15bd95879305415572a4472b1a9","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:58:17Z","oldestEventTime":"2023-10-15T22:58:17Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933************oudTrail_ap-northeast-1_20231015T2300Z_aDYIgZODwysx0Irn.json.gz","hashValue":"de90c3b55016bc5fad9c12378ccc6fc38180a15bd95879305415572a4472b1a9","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:58:17Z","oldestEventTime":"2023-10-15T22:58:17Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2300Z_9eJ8qdKnXIfFg2wM.json.gz","hashValue":"85e79f9b40d5a57be15fa6ac6f54d3ea1919611e37ca682c1e753287ac7b9bcb","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:58:17Z","oldestEventTime":"2023-10-15T22:58:17Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2225Z_OviGSSWadUI1W1r7.json.gz","hashValue":"******","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:20:34Z","oldestEventTime":"2023-10-15T22:10:12Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933************","digestSignatureAlgorithm":"SHA256withRSA","newestEventTime":"2023-10-15T22:58:17Z","oldestEventTime":"2023-10-15T22:04:51Z","previousDigestS3Bucket":"llm-guard-trail","previousDigestS3Object":"AWSLogs\/327878933619\/CloudTrail-Digest\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail-Digest_ap-northeast-1_llm-guard-trail_us-west-2_20231015T220404Z.json.gz","previousDigestHashValue":"******","previousDigestHashAlgorithm":"SHA-256","previousDigestSignature":"******","logFiles":[{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2205Z_iRIoDMA9l9Q4kmFy.json.gz","hashValue":"4309c6161e37538de72ec6f679e86b7e45aebed71fa7e76af70c3019fef44e19","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:04:51Z","oldestEventTime":"2023-10-15T22:04:51Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2300Z_aDYIgZODwysx0Irn.json.gz","hashValue":"de90c3b55016bc5fad9c12378ccc6fc38180a15bd95879305415572a4472b1a9","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:58:17Z************","logFiles":[{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2205Z_iRIoDMA9l9Q4kmFy.json.gz","hashValue":"4309c6161e37538de72ec6f679e86b7e45aebed71fa7e76af70c3019fef44e19","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:04:51Z","oldestEventTime":"2023-10-15T22:04:51Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2300Z_aDYIgZODwysx0Irn.json.gz","hashValue":"de90c3b55016bc5fad9c12378ccc6fc38180a15bd95879305415572a4472b1a9","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:58:17Z","oldestEventTime":"2023-10-15T22:58:17Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2300Z_9eJ8qdKnXIfFg2wM.json.gz","hashValue":"85e79f9b40d5a57be15fa6ac6f54d3ea1919611e37ca682c1e753287ac7b9bcb","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:58:17Z","oldestEventTime":"2023-10-15T22:58:17Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2225Z_OviGSSWadUI1W1r7.json.gz","hashValue":"******","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:20:34Z","oldestEventTime":"2023-10-15T22:10:12Z"},{"s3Bucket":"llm-guard-trail","s3Object":"AWSLogs\/327878933619\/CloudTrail\/ap-northeast-1\/2023\/10\/15\/327878933619_CloudTrail_ap-northeast-1_20231015T2225Z_j5hj9VuYmchJHAkK.json.gz","hashValue":"c18c49161f97def10a14cffa5b5ab441c8fe8194af1cb1d79d470b6173f901c4","hashAlgorithm":"SHA-256","newestEventTime":"2023-10-15T22:20:34Z","oldestEventTime":"2023-10-15T22:20:34Z"}]}',
            False,
            1.0,
        ),  # https://github.com/protectai/llm-guard/issues/147
        (
            "Hello",
            "Hello",
            True,
            0.0,
        ),  # https://github.com/protectai/llm-guard/issues/147
    ],
)
def test_scan(prompt, expected_prompt, expected_valid, expected_score):
    scanner = Secrets()
    sanitized_prompt, valid, score = scanner.scan(prompt)
    print(sanitized_prompt)

    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score
