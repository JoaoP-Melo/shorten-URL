from nanoid import generate


def generator_code_url():
    return generate(size=8)
