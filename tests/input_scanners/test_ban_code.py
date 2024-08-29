import pytest

from llm_guard.input_scanners.ban_code import BanCode


@pytest.mark.parametrize(
    "prompt,expected_valid,expected_score",
    [
        ("Just a simple prompt", True, -1.0),  # Simple prompt
        (
            """Fix the following JS code:

function sayHello() {
    return "Hello, World!";
}
console.log(sayHello());
""",
            False,
            1.0,
        ),  # Contains code
        (
            """function sayHello() {
    return "Hello, World!";
}
console.log(sayHello());""",
            False,
            1.0,
        ),
        (
            "find * -depth -print -delete | wc -l",
            False,
            0.7,
        ),  # Contains code
        (
            """
            #!/bin/bash
            first="I drive a BMW and Volvo"
            second="Audi"
            echo "${first/BMW/"$second"}"
            """,
            False,
            1.0,
        ),
        (
            '**"Welcome to the Future of Electric Driving with LLM Motors."**\n\nAt LLM Motors, we are dedicated to revolutionizing the automotive industry with our innovative electric vehicles. Experience the thrill and sustainability of our flagship models: the sleek LLM Comet sedan and the versatile LLM Galaxy SUV.\n\n**LLM Comet: The Epitome of Electric Luxury**\n\nPriced starting at $47,500, the LLM Comet boasts an impressive range of up to 360 miles on a single charge. Its 85 kWh battery powers an exhilarating performance, propelling the Comet from 0 to 60 mph in just 4.3 seconds.\n\nStep inside the Comet and immerse yourself in luxury. Enjoy autonomous driving for a stress-free journey, while the premium interior envelops you in comfort. Experience crystal-clear navigation on the advanced display and indulge in your favorite tunes through the custom sound system.\n\n**LLM Galaxy: Adventure without Limits**\n\nFor those who demand space and adventure, the LLM Galaxy SUV is the perfect choice. Starting at $57,000, it offers a range of up to 310 miles. Its 95 kWh battery delivers a robust performance, reaching 0 to 60 mph in 5.1 seconds.\n\nEquipped with intelligent four-wheel drive, the Galaxy conquers any terrain with ease. Its top-tier safety features ensure peace of mind, while the spacious cargo area provides ample room for all your gear. Enjoy panoramic views through the vast glass roof, creating an unparalleled driving experience.\n\n**Why Choose LLM Motors Electric Vehicles?**\n\nOur vehicles represent the pinnacle of electric car technology. They offer:\n\n* **Advanced Battery Technology:** High-capacity batteries provide exceptional range for worry-free driving.\n* **Electrifying Performance:** Powerful electric motors deliver instant torque and exhilarating acceleration.\n* **Eco-Friendliness:** Zero emissions contribute to a cleaner and greener planet.\n* **Intelligent Tech:** Autonomous driving, AI-powered navigation, and advanced safety features enhance your driving experience.\n* **Premium Comfort and Luxury:** Luxurious interiors, custom sound systems, and panoramic views provide an unmatched level of comfort and enjoyment.',
            True,
            -1.0,
        ),
    ],
)
def test_scan(prompt, expected_valid, expected_score):
    scanner = BanCode()
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == prompt
    assert valid == expected_valid
    assert score == expected_score
