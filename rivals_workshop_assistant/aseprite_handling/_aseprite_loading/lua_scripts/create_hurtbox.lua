local sprite = app.open(app.params["filename"])

local startFrame = tonumber(app.params["startFrame"])
local endFrame = tonumber(app.params["endFrame"])
local scale = 2

-- Hurtmask layer is subtracted from the hurtbox
local hurtmaskLayer = nil

-- Hurtbox layer, if present, is used as the initial hurtbox
--  (rather than the sprite's silhouette)
local hurtboxLayer = nil

-- All the actual content of the sprite, not special purpose utility layers.
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

-- Deletes frames that aren't in the given range.
local _irrelevantFrames = {}
local _workingFrames = {}
for frameIndex, frame in ipairs(sprite.frames) do
    if startFrame <= frameIndex  and frameIndex <= endFrame then
        table.insert(_workingFrames, frame)
    else
        table.insert(_irrelevantFrames, frame)
    end
end
if #_irrelevantFrames > 0 then
    app.range.frames = _irrelevantFrames
    app.command.RemoveFrame()
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

local hurtmaskSelections = {}
if hurtmaskLayer ~= nil then
    for _, frame in ipairs(sprite.frames) do
        local selection = select_content(hurtmaskLayer, frame)
        table.insert(hurtmaskSelections, selection)
    end
    app.range.layers = { hurtmaskLayer }
    app.command.removeLayer()
end

if hurtboxLayer ~= nil then
    hurtboxLayer.isVisible = False
end


-- Flatten content_layers.
app.range.layers = content_layers
app.command.FlattenLayers {
    visibleOnly = True
}

-- Get content_layer
local content_layer = nil
for _, layer in ipairs(sprite.layers) do
    if layer.name == "Flattened" then
        content_layer = layer
    end
end
assert(content_layer ~= nil, "no layer called Flattened")


app.activeLayer = content_layer
for i = 1, #hurtmaskSelections do
    local layer = sprite.layers[i]
    local selection = hurtmaskSelections[i]

    app.range.layers = {layer}
    sprite.selection = selection

    app.command.ReplaceColor {
        ui=false,
        from=Color{r=255, g=255, b=255, a=255},
        to=Color{ r=0, g=0, b=0, a=0},
        tolerance=255
    }
    app.command.DeselectMask()
end


for _, frame in ipairs(sprite.frames) do
    app.activeFrame = frame

    app.activeLayer = content_layer
    sprite.selection = select_content(content_layer, frame)

    app.command.ReplaceColor {
        ui=false,
        from=Color{ r=255, g=255, b=255, a=255 },
        to=Color{ r=0, g=255, b=0, a=255 },
        tolerance=255
    }
    app.command.DeselectMask()
end

app.command.SpriteSize {
    scale=scale
}

app.command.ExportSpriteSheet {
    ui=false,
    askOverwrite=false,
    type=SpriteSheetType.HORIZONTAL,
    textureFilename=app.params["dest"],
}
