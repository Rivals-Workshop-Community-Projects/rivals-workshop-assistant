--app.command.DeveloperConsole()

local start_frame = 1
local end_frame = 3



local sprite = app.activeSprite
if not sprite then
    return
end

local function is_hurtmask(layer)
    return layer.name == "HURTMASK"
end

local function is_non_transparent(pixel)
    return pixel() > 0
    --return app.pixelColor.rgbaA(pixel) ~= 0
    --        or app.pixelColor.grayaA(pixel) ~= 0
end

local function select_content(layer, frameNumber)
    local cel = layer:cel(frameNumber)
    if cel == nil then
        return Selection()
    end

    local points = {}
    for pixel in cel.image:pixels() do
        --local pixelValue = pixel() -- get pixel
        --if app.pixelColor.rgbaA(pixelValue) > 0 then
        if is_non_transparent(pixel) then
            table.insert(points, Point(pixel.x + cel.position.x, pixel.y + cel.position.y))
        end
    end

    local select = Selection()
    for _, point in ipairs(points) do
        local pixel_rect = Rectangle(point.x, point.y, 1, 1)
        select:add(Selection(pixel_rect))
    end
    return select
end

--app.transaction(function()
    -- Get hurtmask_layer and content_layers
    local hurtmask_layer = nil
    local content_layers = {}
    for _, layer in ipairs(sprite.layers) do
        if is_hurtmask(layer) then
            hurtmask_layer = layer
        else
            if layer.isVisible then
                table.insert(content_layers, layer)
            else
                app.range.layers = { layer }
                app.command.removeLayer()
            end
        end
    end

    hurtmask_layer.isVisible = false

    -- Flatten content_layers.
    app.range.layers = content_layers
    app.command.FlattenLayers()

    for frame = start_frame, end_frame do
        app.activeFrame = frame

        -- Get content_layer
        local content_layer = nil
        for _, layer in ipairs(sprite.layers) do
            if layer.name == "Flattened" then
                content_layer = layer
            end
        end
        assert(content_layer ~= nil, "no layer called Flattened")

        sprite.selection = select_content(hurtmask_layer, frame)

        app.activeLayer = content_layer

        app.command.ReplaceColor {
            ui=false,
            to=Color{ r=0, g=0, b=0, a=0 },
            tolerance=255
        }

        print(content_layer)

        sprite.selection = select_content(content_layer, frame)


        app.command.ReplaceColor {
            ui=false,
            to=Color{ r=0, g=255, b=0 },
            tolerance=255
        }

        app.command.DeselectMask()

    end




    -- delete the selection from the content
    -- delete. Then unselect
    -- Turn green!
    -- Edit fill with the green color
    -- Save

--end
--)
