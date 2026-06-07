# Visual constants — calibrated from ref_001 frame analysis

# Canvas
CANVAS_W = 1080
CANVAS_H = 1920
FPS = 30

# Colors
BG_COLOR = "#000000"
STROKE_COLOR = "#FFFFFF"
TITLE_COLOR = "#FFFFFF"
WORD_COLOR = "#FFFFFF"

# Scene panel (cinematic 16:9 window centered in 9:16 frame)
PANEL_W = 960          # px within 1080 canvas
PANEL_H = 540          # 16:9 ratio
PANEL_Y_CENTER = 1020  # vertical center in 1920 canvas (slightly below middle)

# Stroke
STROKE_WIDTH = 5        # Manim stroke width
STROKE_OPACITY = 1.0

# Glow post-process (OpenCV)
GLOW_BLUR_RADIUS = 21   # must be odd — size of gaussian kernel
GLOW_INTENSITY = 1.8    # multiplier applied to blurred layer before screen blend
GLOW_PASSES = 2         # number of blur passes (more = softer, wider halo)

# Background grain
NOISE_INTENSITY = 12    # 0-255, subtle texture on black bg

# Typography — title
TITLE_FONT = "Arial"
TITLE_FONT_SIZE = 68
TITLE_BOLD = True
TITLE_X = 90            # px from left edge
TITLE_Y = 340           # px from top

# Typography — word subtitles
WORD_FONT = "Arial"
WORD_FONT_SIZE = 44
WORD_Y_OFFSET = 30      # px below panel bottom edge

# Timing
DEFAULT_SCENE_DURATION = 10.0   # seconds per scene if not overridden
DRAW_SPEED = 1.2                # Manim run_time multiplier for Create() animations
IMPACT_FLASH_DURATION = 0.3     # seconds for star-burst flash effect
