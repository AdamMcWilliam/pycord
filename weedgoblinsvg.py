import cairo

def draw_weedgoblin(ctx):
    ctx.set_line_width(2)

    # Weedgoblin head
    ctx.arc(250, 250, 100, 0, 2 * 3.14159)
    ctx.set_source_rgb(0, 1, 0)
    ctx.fill_preserve()
    ctx.set_source_rgb(0, 0, 0)
    ctx.stroke()

    # Weedgoblin ears
    ctx.move_to(150, 250)
    ctx.curve_to(100, 200, 100, 300, 150, 250)
    ctx.line_to(350, 250)
    ctx.curve_to(400, 300, 400, 200, 350, 250)
    ctx.close_path()
    ctx.set_source_rgb(0, 1, 0)
    ctx.fill_preserve()
    ctx.set_source_rgb(0, 0, 0)
    ctx.stroke()

    # Weedgoblin eyes
    ctx.arc(210, 230, 20, 0, 2 * 3.14159)
    ctx.arc(290, 230, 20, 0, 2 * 3.14159)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill_preserve()
    ctx.set_source_rgb(0, 0, 0)
    ctx.stroke()

    # Weedgoblin pupils
    ctx.arc(210, 230, 10, 0, 2 * 3.14159)
    ctx.arc(290, 230, 10, 0, 2 * 3.14159)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()

    # Weedgoblin mouth
    ctx.move_to(200, 300)
    ctx.curve_to(250, 330, 250, 330, 300, 300)
    ctx.set_source_rgb(0, 0, 0)
    ctx.stroke()

    # Weedgoblin joint
    ctx.move_to(250, 330)
    ctx.line_to(320, 380)
    ctx.set_source_rgb(0.5, 0.25, 0)
    ctx.set_line_width(5)
    ctx.stroke()

    # Blue Dream smoke
    ctx.move_to(320, 380)
    ctx.curve_to(340, 360, 360, 370, 360, 340)
    ctx.set_source_rgb(0, 0, 1)
    ctx.set_line_width(5)
    ctx.stroke()

def create_weedgoblin_png(filename):
    width, height = 500, 500
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    draw_weedgoblin(ctx)
    surface.write_to_png(filename)

create_weedgoblin_png("weedgoblin.png")