from pathlib import Path

import pytest

from rivals_workshop_assistant import code_generation as src

PATH_A = Path('a')


@pytest.mark.parametrize(
    'original_content, expected_content',
    [
        pytest.param('nothing to do', 'nothing to do'),
        pytest.param('before$bad$after',
                     'before$bad$after // ERROR: No code injection match found'),
        pytest.param('before$foreach things', 'before$foreach things'),
        pytest.param('foreach things$', 'foreach things$'),
        pytest.param('a//$foreach things$b', 'a//$foreach things$b'),
        pytest.param('$foreach alist$', '''\
for (var alist_item_i = 0; alist_item_i++; alist_item_i < array_length(alist) {
    var alist_item = alist[alist_item_i]
}'''),
        pytest.param('$foreach blah$', '''\
for (var blah_item_i = 0; blah_item_i++; blah_item_i < array_length(blah) {
    var blah_item = blah[blah_item_i]
}'''),
        pytest.param('    $foreach blah$', '''\
    for (var blah_item_i = 0; blah_item_i++; blah_item_i < array_length(blah) {
        var blah_item = blah[blah_item_i]
    }'''),
        pytest.param('$foreach things$', '''\
for (var thing_i = 0; thing_i++; thing_i < array_length(things) {
    var thing = things[thing_i]
}'''),
    ]

)
def test_handle_codegen__for_loop(original_content, expected_content):
    scripts = {PATH_A: original_content}

    result = src.handle_codegen(scripts)

    assert result == {PATH_A: expected_content}
