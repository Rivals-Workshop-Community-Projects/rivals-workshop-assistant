local sprite = app.open(app.params["filename"])

local startFrame = tonumber(app.params["startFrame"])
local endFrame = tonumber(app.params["endFrame"])
local scale = 2

local hurtmaskLayer = nil
local hurtboxLayer = nil
local content_layers = {}
for _, layer in ipairs(sprite.layers) do
    if layer.name == "HURTMASK" then
        hurtmaskLayer = layer
    elseif layer.name == "HURTBOX" then
        hurtboxLayer = layer
    else
        if layer.isVisible then
            table.insert(content_layers, layer)
        else
            app.range.layers = { layer }
            app.command.removeLayer()
        end
    end
end

local irrelevantFrames = {}
local workingFrames = {}
for frameIndex, frame in ipairs(sprite.frames) do
    if startFrame <= frameIndex  and frameIndex <= endFrame then
        table.insert(workingFrames, frame)
    else
        table.insert(irrelevantFrames, frame)
    end
end

if #irrelevantFrames > 0 then
    app.range.frames = irrelevantFrames
    app.command.RemoveFrame()
end


app.activeSprite = sprite

app.command.SpriteSize {
    scaleX=scale,
    scaleY=scale,
}


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

if hurtmaskLayer ~= nill then
    hurtmaskLayer.isVisible = false
end
if hurtboxLayer ~= nill then
    hurtboxLayer.isVisible = false
end


-- Flatten content_layers.
app.range.layers = content_layers
app.command.FlattenLayers()

for _, frame in ipairs(sprite.frames) do
    app.activeFrame = frame

    -- Get content_layer
    local content_layer = nil
    for _, layer in ipairs(sprite.layers) do
        if layer.name == "Flattened" then
            content_layer = layer
        end
    end
    assert(content_layer ~= nil, "no layer called Flattened")

    if hurtmaskLayer ~= nil then
        sprite.selection = select_content(hurtmaskLayer, frame)
        app.activeLayer = content_layer

        app.command.ReplaceColor {
            ui=false,
            to=Color{ r=0, g=0, b=0, a=0 },
            tolerance=255
        }
    end

    app.activeLayer = content_layer
    sprite.selection = select_content(content_layer, frame)

    app.command.ReplaceColor {
        ui=false,
        to=Color{ r=0, g=255, b=0 },
        tolerance=255
    }
    app.command.DeselectMask()
end

app.command.ExportSpriteSheet {
    ui=false,
    askOverwrite=false,
    type=SpriteSheetType.HORIZONTAL,
    textureFilename=app.params["dest"],
}
