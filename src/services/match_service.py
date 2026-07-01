def run_match():
    # Delegate to existing legacy matcher implementation for now.
    from legacy import matcher as legacy_matcher
    return legacy_matcher.run_matcher()

