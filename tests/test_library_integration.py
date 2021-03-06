# TODO first load scripts, then load injections, then apply injections
#
# def test_read_injection_library():
#     with TempDirectory() as dir:
#
#         dir.write(Path('inject/test.gml'), """\
# #define name
#     content""")
#
#         read_injection_library()
#
#         foo2bar(dir.path, 'test.txt')
#         dir.read('test.txt')
#         assert False
