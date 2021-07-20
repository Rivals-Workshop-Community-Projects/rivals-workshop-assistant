local sprite = app.open(app.params["filename"])

local startFrame = tonumber(app.params["startFrame"])
local endFrame = tonumber(app.params["endFrame"])
local scale = tonumber(app.params["scale"])

for _, layer in ipairs(sprite.layers) do
    if layer.name == "HURTMASK" or layer.name == "HURTBOX" then
        app.range.layers = { layer }
        app.command.removeLayer()
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

app.command.ExportSpriteSheet {
    ui=false,
    askOverwrite=false,
    type=SpriteSheetType.HORIZONTAL,
    textureFilename=app.params["dest"],
}