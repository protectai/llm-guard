from typing import Dict, List, Optional

from llm_guard.util import get_logger

LOGGER = get_logger()

DEFAULT_REGEX_PATTERNS = [
    {
        "expressions": [
            r"(?:(4\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})|(3[47]\d{2}[-\s]?\d{6}[-\s]?\d{5})|(3(?:0[0-5]|[68]\d)\d{11}))"
        ],
        "name": "CREDIT_CARD_RE",
        "examples": ["4111111111111111", "378282246310005", "30569309025904"],
        "context": [],
        "score": 0.75,
        "languages": ["en", "zh"],
    },
    {
        "expressions": [r"[a-f0-9]{8}\-[a-f0-9]{4}\-[a-f0-9]{4}\-[a-f0-9]{4}\-[a-f0-9]{12}"],
        "name": "UUID",
        "examples": ["550e8400-e29b-41d4-a716-446655440000"],
        "context": [],
        "score": 0.75,
        "languages": ["en", "zh"],
    },
    {
        "expressions": [r"\b[A-Za-z0-9._%+-]+(\[AT\]|@)[A-Za-z0-9.-]+(\[DOT\]|\.)[A-Za-z]{2,}\b"],
        "name": "EMAIL_ADDRESS_RE",
        "examples": [
            "john.doe@protectai.com",
            "john.doe[AT]protectai[DOT]com",
            "john.doe[AT]protectai.com",
            "john.doe@protectai[DOT]com",
        ],
        "context": [],
        "score": 0.75,
        "languages": ["en", "zh"],
    },
    {
        "expressions": [r"\b\d{3}-\d{2}-\d{4}\b"],
        "name": "US_SSN_RE",
        "examples": ["111-22-3333", "987-65-4321"],
        "context": [],
        "score": 0.75,
        "languages": ["en"],
    },
    {
        "expressions": [
            r"(?<![a-km-zA-HJ-NP-Z0-9])[13][a-km-zA-HJ-NP-Z0-9]{26,33}(?![a-km-zA-HJ-NP-Z0-9])"
        ],
        "name": "BTC_ADDRESS",
        "examples": [
            "1LgqButDNV2rVHe9DATt6WqD8tKZEKvaK2",
            "19P6EYhu6kZzRy9Au4wRRZVE8RemrxPbZP",
            "1bones8KbQge9euDn523z5wVhwkTP3uc1",
            "1Bow5EMqtDGV5n5xZVgdpRPJiiDK6XSjiC",
        ],
        "context": [],
        "score": 0.75,
        "languages": ["en"],
    },
    {
        "expressions": [
            r"(?i)((?:https?://|www\d{0,3}[.])?[a-z0-9.\-]+[.](?:(?:international)|(?:construction)|(?:contractors)|(?:enterprises)|(?:photography)|(?:immobilien)|(?:management)|(?:technology)|(?:directory)|(?:education)|(?:equipment)|(?:institute)|(?:marketing)|(?:solutions)|(?:builders)|(?:clothing)|(?:computer)|(?:democrat)|(?:diamonds)|(?:graphics)|(?:holdings)|(?:lighting)|(?:plumbing)|(?:training)|(?:ventures)|(?:academy)|(?:careers)|(?:company)|(?:domains)|(?:florist)|(?:gallery)|(?:guitars)|(?:holiday)|(?:kitchen)|(?:recipes)|(?:shiksha)|(?:singles)|(?:support)|(?:systems)|(?:agency)|(?:berlin)|(?:camera)|(?:center)|(?:coffee)|(?:estate)|(?:kaufen)|(?:luxury)|(?:monash)|(?:museum)|(?:photos)|(?:repair)|(?:social)|(?:tattoo)|(?:travel)|(?:viajes)|(?:voyage)|(?:build)|(?:cheap)|(?:codes)|(?:dance)|(?:email)|(?:glass)|(?:house)|(?:ninja)|(?:photo)|(?:shoes)|(?:solar)|(?:today)|(?:aero)|(?:arpa)|(?:asia)|(?:bike)|(?:buzz)|(?:camp)|(?:club)|(?:coop)|(?:farm)|(?:gift)|(?:guru)|(?:info)|(?:jobs)|(?:kiwi)|(?:land)|(?:limo)|(?:link)|(?:menu)|(?:mobi)|(?:moda)|(?:name)|(?:pics)|(?:pink)|(?:post)|(?:rich)|(?:ruhr)|(?:sexy)|(?:tips)|(?:wang)|(?:wien)|(?:zone)|(?:biz)|(?:cab)|(?:cat)|(?:ceo)|(?:com)|(?:edu)|(?:gov)|(?:int)|(?:mil)|(?:net)|(?:onl)|(?:org)|(?:pro)|(?:red)|(?:tel)|(?:uno)|(?:xxx)|(?:ac)|(?:ad)|(?:ae)|(?:af)|(?:ag)|(?:ai)|(?:al)|(?:am)|(?:an)|(?:ao)|(?:aq)|(?:ar)|(?:as)|(?:at)|(?:au)|(?:aw)|(?:ax)|(?:az)|(?:ba)|(?:bb)|(?:bd)|(?:be)|(?:bf)|(?:bg)|(?:bh)|(?:bi)|(?:bj)|(?:bm)|(?:bn)|(?:bo)|(?:br)|(?:bs)|(?:bt)|(?:bv)|(?:bw)|(?:by)|(?:bz)|(?:ca)|(?:cc)|(?:cd)|(?:cf)|(?:cg)|(?:ch)|(?:ci)|(?:ck)|(?:cl)|(?:cm)|(?:cn)|(?:co)|(?:cr)|(?:cu)|(?:cv)|(?:cw)|(?:cx)|(?:cy)|(?:cz)|(?:de)|(?:dj)|(?:dk)|(?:dm)|(?:do)|(?:dz)|(?:ec)|(?:ee)|(?:eg)|(?:er)|(?:es)|(?:et)|(?:eu)|(?:fi)|(?:fj)|(?:fk)|(?:fm)|(?:fo)|(?:fr)|(?:ga)|(?:gb)|(?:gd)|(?:ge)|(?:gf)|(?:gg)|(?:gh)|(?:gi)|(?:gl)|(?:gm)|(?:gn)|(?:gp)|(?:gq)|(?:gr)|(?:gs)|(?:gt)|(?:gu)|(?:gw)|(?:gy)|(?:hk)|(?:hm)|(?:hn)|(?:hr)|(?:ht)|(?:hu)|(?:id)|(?:ie)|(?:il)|(?:im)|(?:in)|(?:io)|(?:iq)|(?:ir)|(?:is)|(?:it)|(?:je)|(?:jm)|(?:jo)|(?:jp)|(?:ke)|(?:kg)|(?:kh)|(?:ki)|(?:km)|(?:kn)|(?:kp)|(?:kr)|(?:kw)|(?:ky)|(?:kz)|(?:la)|(?:lb)|(?:lc)|(?:li)|(?:lk)|(?:lr)|(?:ls)|(?:lt)|(?:lu)|(?:lv)|(?:ly)|(?:ma)|(?:mc)|(?:md)|(?:me)|(?:mg)|(?:mh)|(?:mk)|(?:ml)|(?:mm)|(?:mn)|(?:mo)|(?:mp)|(?:mq)|(?:mr)|(?:ms)|(?:mt)|(?:mu)|(?:mv)|(?:mw)|(?:mx)|(?:my)|(?:mz)|(?:na)|(?:nc)|(?:ne)|(?:nf)|(?:ng)|(?:ni)|(?:nl)|(?:no)|(?:np)|(?:nr)|(?:nu)|(?:nz)|(?:om)|(?:pa)|(?:pe)|(?:pf)|(?:pg)|(?:ph)|(?:pk)|(?:pl)|(?:pm)|(?:pn)|(?:pr)|(?:ps)|(?:pt)|(?:pw)|(?:py)|(?:qa)|(?:re)|(?:ro)|(?:rs)|(?:ru)|(?:rw)|(?:sa)|(?:sb)|(?:sc)|(?:sd)|(?:se)|(?:sg)|(?:sh)|(?:si)|(?:sj)|(?:sk)|(?:sl)|(?:sm)|(?:sn)|(?:so)|(?:sr)|(?:st)|(?:su)|(?:sv)|(?:sx)|(?:sy)|(?:sz)|(?:tc)|(?:td)|(?:tf)|(?:tg)|(?:th)|(?:tj)|(?:tk)|(?:tl)|(?:tm)|(?:tn)|(?:to)|(?:tp)|(?:tr)|(?:tt)|(?:tv)|(?:tw)|(?:tz)|(?:ua)|(?:ug)|(?:uk)|(?:us)|(?:uy)|(?:uz)|(?:va)|(?:vc)|(?:ve)|(?:vg)|(?:vi)|(?:vn)|(?:vu)|(?:wf)|(?:ws)|(?:ye)|(?:yt)|(?:za)|(?:zm)|(?:zw))(?:/[^\s()<>]+[^\s`!()\[\]{};:\'\".,<>?\xab\xbb\u201c\u201d\u2018\u2019])?)"
        ],
        "name": "URL_RE",
        "examples": ["http://www.protectai.com", "https://protectai.com", "www.protectai.com"],
        "context": [],
        "score": 0.75,
        "languages": ["en"],
    },
    {
        "name": "CREDIT_CARD",
        "reuse": {"language": "en", "name": "CREDIT_CARD"},
        "languages": ["zh"],
    },
    {
        "expressions": [r"[A-Za-z0-9._%+-]+(\[AT\]|@)[A-Za-z0-9.-]+(\[DOT\]|\.)[A-Za-z]{2,}"],
        "name": "EMAIL_ADDRESS_RE",
        "examples": [
            "john.doe@protectai.com",
            "john.doe[AT]protectai[DOT]com",
            "john.doe[AT]protectai.com",
            "john.doe@protectai[DOT]com",
        ],
        "context": [],
        "score": 0.75,
        "languages": ["zh"],
    },
    {
        "expressions": [r"(13[0-9]|14[5-9]|15[0-3,5-9]|16[6]|17[0-8]|18[0-9]|19[8,9])\d{8}"],
        "name": "PHONE_NUMBER_ZH",
        "examples": ["13011112222", "14922223333"],
        "context": ["phone", "number", "telephone", "cell", "cellphone", "mobile", "call"],
        "score": 0.75,
        "languages": ["zh"],
    },
    {
        "expressions": [
            r"(?i)((?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*(?:[2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|(?:[2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?(?:[2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?(?:[0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(?:\d+)?))"
        ],
        "name": "PHONE_NUMBER_WITH_EXT",
        "examples": [
            "(523)222-8888 ext 527",
            "(523)222-8888x623",
            "(523)222-8888 x623",
            "(523)222-8888 x 623",
            "(523)222-8888EXT623",
            "523-222-8888EXT623",
            "(523) 222-8888 x 623",
        ],
        "context": [],
        "score": 0.75,
        "languages": ["en"],
    },
    {
        "expressions": [
            r"(?i)(?:(?<!\:)(?<!\:\d)[0-3]?\d(?:st|nd|rd|th)?\s+(?:of\s+)?(?:jan\.?|january|feb\.?|february|mar\.?|march|apr\.?|april|may|jun\.?|june|jul\.?|july|aug\.?|august|sep\.?|september|oct\.?|october|nov\.?|november|dec\.?|december)|(?:jan\.?|january|feb\.?|february|mar\.?|march|apr\.?|april|may|jun\.?|june|jul\.?|july|aug\.?|august|sep\.?|september|oct\.?|october|nov\.?|november|dec\.?|december)\s+(?<!\:)(?<!\:\d)[0-3]?\d(?:st|nd|rd|th)?)(?:\,)?\s*(?:\d{4})?|[0-3]?\d[-\./][0-3]?\d[-\./]\d{2,4}"
        ],
        "name": "DATE_RE",
        "examples": [
            "12-31-2024",
            "12/31/2024",
            "3 of April 2021",
            "3rd of April 2021",
            "November 30th 2021",
            "November 30 2021",
            "4th July, 2022",
        ],
        "context": ["date", "time", "month", "year"],
        "score": 0.75,
        "languages": ["en"],
    },
    {
        "expressions": [r"(?i)\d{1,2}:\d{2} ?(?:[ap]\.?m\.?)?|\d[ap]\.?m\.?"],
        "name": "TIME_RE",
        "examples": ["12:00 PM", "12:00PM", "12:00 pm", "12:00pm", "12:00", "12pm"],
        "context": ["time"],
        "score": 0.75,
        "languages": ["en"],
    },
    {
        "expressions": [r"(#(?:[0-9a-fA-F]{8})|#(?:[0-9a-fA-F]{3}){1,2})\b"],
        "name": "HEX_COLOR",
        "examples": ["#ff0000", "#f00"],
        "context": ["color", "code"],
        "score": 0.75,
        "languages": ["en"],
    },
    {
        "expressions": [r"[$]\s?[+-]?[0-9]{1,3}(?:(?:,?[0-9]{3}))*(?:\.[0-9]{1,2})?"],
        "name": "PRICE_RE",
        "examples": ["$1.23", "$1", "$1,000", "$10,000.00"],
        "context": ["price", "money", "cost", "value", "amount"],
        "score": 0.75,
        "languages": ["en"],
    },
    {
        "expressions": [r"(?i)P\.? ?O\.? Box \d+"],
        "name": "PO_BOX_RE",
        "examples": ["PO Box 123456", "hey p.o. box 234234 hey"],
        "context": ["address", "mail", "post", "box"],
        "score": 0.75,
        "languages": ["en"],
    },
]


def get_regex_patterns(regex_patterns: Optional[List[Dict]] = None) -> List[Dict]:
    if not regex_patterns:
        regex_patterns = DEFAULT_REGEX_PATTERNS

    result = []
    for group in regex_patterns:
        result.append(
            {
                "name": group["name"].upper(),
                "expressions": group.get("expressions", []),
                "context": group.get("context", []),
                "score": group.get("score", 0.75),
                "languages": group.get("languages", ["en"]),
                "reuse": group.get("reuse", False),
            }
        )
        LOGGER.debug("Loaded regex pattern", group_name=group["name"])

    return result
