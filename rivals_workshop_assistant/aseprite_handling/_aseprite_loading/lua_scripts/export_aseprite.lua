

local sprite = app.open(app.params["filename"])

local startFrame = tonumber(app.params["startFrame"])
local endFrame = tonumber(app.params["endFrame"])
local scale = tonumber(app.params["scale"])

local irrelevantFrames = {}
local workingFrames = {}
--for frameIndex = startFrame, endFrame do
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
    --columns=5,
    --rows=0,
    --width=0,
    --height=0,
    --dataFilename=app.params["dest"],
    textureFilename=app.params["dest"],
}