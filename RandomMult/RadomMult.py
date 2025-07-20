
import turtle
import random
import time
import svgwrite

def setup_canvas():
    screen = turtle.Screen()
    screen.title("Smooth Jittered Stripes")
    screen.bgcolor("black")
    screen.setworldcoordinates(-200, -200, 200, 200)
    turtle.speed(0)
    turtle.hideturtle()
    turtle.pensize(1)
    screen.tracer(0, 0)
    return screen

def smooth_list(values, window=7):
    n, half = len(values), window//2
    sm = []
    for i in range(n):
        lo, hi = max(0, i-half), min(n, i+half+1)
        sm.append(sum(values[lo:hi])/(hi-lo))
    return sm

def draw_smooth_jittered_stripes(lines=300, steps=300):
    x0, x1 = -200, 200
    total_height = 400
    spacing = total_height / (lines - 1)
    # jitter grows with stripe index, but never exceeds 80% of spacing
    max_jitter_per_stripe = spacing * 0.8

    xs = [x0 + i*(x1-x0)/(steps-1) for i in range(steps)]
    ys_prev = [200]*steps  # first stripe at y=200

    # Prepare SVG drawing
    svg_size = 400
    dwg = svgwrite.Drawing('smooth_jittered_stripes.svg', size=(svg_size, svg_size), profile='tiny')
    svg_y_offset = 200
    svg_x_offset = 200

    for i in range(lines):
        # compute and cap jitter amplitude
        amp = min(i * 0.1, max_jitter_per_stripe)

        # generate raw ys, then clamp so y <= (prev_y - spacing*0.1)
        raw = []
        for prev_y in ys_prev:
            target = prev_y - spacing
            y = target + random.uniform(-amp, amp)
            # ensure a minimum gap of 10% of spacing
            min_allowed = prev_y - spacing + (spacing * 0.1)
            raw.append(min(y, min_allowed))

        ys = smooth_list(raw, window=7)

        # fade from white → dark
        gray = 1.0 - (i/(lines-1))*0.8
        gray = max(0.0, min(1.0, gray))
        turtle.pencolor(gray, gray, gray)

        # Prepare SVG color (convert gray to hex)
        gray255 = int(gray * 255)
        hexcol = f'#{gray255:02x}{gray255:02x}{gray255:02x}'

        # Draw on screen
        turtle.penup()
        turtle.goto(xs[0], ys[0])
        turtle.pendown()
        for x, y in zip(xs, ys):
            turtle.goto(x, y)
            turtle.getscreen().update()
            time.sleep(0.0002)
        turtle.penup()

        # Add to SVG
        svg_points = [((x + svg_x_offset), (svg_y_offset - y)) for x, y in zip(xs, ys)]
        dwg.add(dwg.polyline(points=svg_points, stroke=hexcol, fill='none', stroke_width=2))

        ys_prev = ys  # next stripe will base itself on this one

    # Save SVG after all stripes
    dwg.save()
    print("Image saved as smooth_jittered_stripes.svg")

def main():
    screen = setup_canvas()
    draw_smooth_jittered_stripes()
    # Save the canvas as a postscript file, then convert to TIFF
    canvas = screen.getcanvas()
    ps_file = "smooth_jittered_stripes.eps"
    tiff_file = "smooth_jittered_stripes.tiff"
    canvas.postscript(file=ps_file)
    print(f"Image saved as {ps_file}")
    try:
        from PIL import Image
        img = Image.open(ps_file)
        img.save(tiff_file, format='TIFF')
        print(f"Image saved as {tiff_file}")
    except ImportError:
        print("Pillow (PIL) is not installed. TIFF conversion skipped.")
    except Exception as e:
        print(f"TIFF conversion failed: {e}")
    screen.exitonclick()

if __name__ == "__main__":
    main()
