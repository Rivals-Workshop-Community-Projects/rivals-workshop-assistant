import pytest
from PIL import Image, ImageDraw, ImageChops

import rivals_workshop_assistant.asset_handling.sprite_generation as src


def make_canvas(width, height):
    return Image.new('RGBA', (width, height))


def show_delta(img1, img2):
    diff = Image.new("RGB", img1.size, (255, 255, 255))
    for x1 in range(img1.size[0]):
        for y1 in range(img1.size[1]):
            x2 = img1.size[0] - 1 - x1
            y2 = img1.size[1] - 1 - y1

            p1 = img1.getpixel((x1, y1))
            p2 = img2.getpixel((x2, y2))
            p3 = round((p1[0] / 2) - (p2[0] / 2)) + 128

            diff.putpixel((x1, y1), (p3, p3, p3))

    img1.show()
    img2.show()
    diff.show()


def assert_images_equal(img1, img2):
    assert not ImageChops.difference(img1,
                                     img2).getbbox()


@pytest.mark.parametrize(
    'size',
    [
        pytest.param(22),
        pytest.param(43)
    ]
)
def test__generate_sprite_for_file_name__circle(size):
    file_name = f"circle_{size}.png"

    result = src.generate_sprite_for_file_name(file_name)

    expected = make_canvas(size, size)
    ImageDraw.Draw(expected).ellipse((0, 0, size - 1, size - 1),
                                     outline="black")
    assert_images_equal(result, expected)


@pytest.mark.parametrize(
    'color, size',
    [
        pytest.param("red", 25),
        pytest.param("blue", 199)
    ]
)
def test__generate_sprite_for_file_name__circle_colored(color, size):
    file_name = f"{color}_circle_{size}.png"

    result = src.generate_sprite_for_file_name(file_name)

    expected = make_canvas(size, size)
    ImageDraw.Draw(expected).ellipse((0, 0, size - 1, size - 1),
                                     fill=color,
                                     outline="black")
    assert_images_equal(result, expected)


@pytest.mark.parametrize(
    'width, height',
    [
        pytest.param(25, 15),
        pytest.param(10, 100)
    ]
)
def test__generate_sprite_for_file_name__ellipse(width, height):
    file_name = f"ellipse_{width}_{height}.png"

    result = src.generate_sprite_for_file_name(file_name)

    expected = make_canvas(width, height)
    ImageDraw.Draw(expected).ellipse((0, 0, width - 1, height - 1),
                                     outline="black")
    assert_images_equal(result, expected)


@pytest.mark.parametrize(
    'color, width, height',
    [
        pytest.param('orange', 5, 10),
        pytest.param('blue', 66, 55)
    ]
)
def test__generate_sprite_for_file_name__ellipse_colored(color, width, height):
    file_name = f"{color}_ellipse_{width}_{height}.png"

    result = src.generate_sprite_for_file_name(file_name)

    expected = make_canvas(width, height)
    ImageDraw.Draw(expected).ellipse((0, 0, width - 1, height - 1),
                                     fill=color,
                                     outline="black")
    assert_images_equal(result, expected)


@pytest.mark.parametrize(
    'width, height',
    [
        pytest.param(12, 55),
        pytest.param(100, 300)
    ]
)
def test__generate_sprite_for_file_name__rect(width, height):
    file_name = f"rect_{width}_{height}.png"

    result = src.generate_sprite_for_file_name(file_name)

    expected = make_canvas(width, height)
    ImageDraw.Draw(expected).rectangle((0, 0, width - 1, height - 1),
                                       outline="black")
    assert_images_equal(result, expected)


@pytest.mark.parametrize(
    'color, width, height',
    [
        pytest.param('orange', 51, 4),
        pytest.param('blue', 305, 511)
    ]
)
def test__generate_sprite_for_file_name__rect_colored(color, width, height):
    file_name = f"{color}_rect_{width}_{height}.png"

    result = src.generate_sprite_for_file_name(file_name)

    expected = make_canvas(width, height)
    ImageDraw.Draw(expected).rectangle((0, 0, width - 1, height - 1),
                                       fill=color,
                                       outline="black")
    assert_images_equal(result, expected)


@pytest.mark.parametrize(
    'file_name',
    [
        pytest.param('whatever'),
        pytest.param('circle_rect_ellipse'),
        pytest.param('circle_10_10'),
        pytest.param('ellipse_30'),
        pytest.param('red_blue_rect_30_30'),
        pytest.param('blue_rect_30_30_30'),
        pytest.param('rect_30_30_30'),
        pytest.param('rect_blue_30_30'),
    ]
)
def test__generate_sprite_for_file_name__unrelated_file_names(file_name):
    result = src.generate_sprite_for_file_name(file_name)
    assert result is None


"""
"rect_34_36.png"
"orange_rect_3_5.png"
unrelated names
"""
