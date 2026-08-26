from token_trimmer import HybridTokenTrimmer

def test_trimmer():
    # Set a tiny max_tokens limit to force the truncation logic to trigger
    trimmer = HybridTokenTrimmer(max_tokens=20) 
    
    # Large bloated HTML with styles and scripts that should be stripped
    html = """
    <html>
    <head><style>body {color: red;}</style><script>alert('test');</script></head>
    <body>
        <h1>Hello World</h1>
        <p>This is a massively bloated paragraph that we want to ensure gets completely truncated because it exceeds the extremely small max tokens limit we just set for this test case. If it doesn't truncate, something is wrong with our hybrid estimator.</p>
    </body>
    </html>
    """
    
    result = trimmer.process(html)
    print("--- RAW RESULT ---")
    print(result)
    
    assert "body {color: red;}" not in result, "Style tags were not stripped!"
    assert "alert('test');" not in result, "Script tags were not stripped!"
    
    if "[!WARNING]" in result:
        print("\n[SUCCESS] Trimmer successfully stripped HTML, triggered local estimation, truncated the text, and appended the warning!")
    else:
        print("\n[FAILED] Trimmer did not truncate as expected.")

if __name__ == "__main__":
    test_trimmer()
