from retile import test_files as f, test_common as c, test_metadata as m

def run_tests():
    c.run_tests()
    m.run_tests()
    f.run_tests()

if __name__ == '__main__':
    run_tests()