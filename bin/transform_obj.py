#!/usr/bin/env python3
"""
OBJ 3D Model Transformer with Translation
Scale, rotate, and translate OBJ files.
"""

import sys
import argparse
import math


def read_obj_file(filename):
    """Read OBJ file and extract vertices and all other lines."""
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file not found: {filename}")
        sys.exit(1)

    vertices = []
    other_lines = []

    for line in lines:
        line = line.strip()
        if line.startswith('v '):
            parts = line.split()
            if len(parts) >= 4:
                try:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    vertices.append((x, y, z))
                    other_lines.append(('vertex', len(vertices) - 1))
                except ValueError:
                    print(f"Error: Invalid vertex: {line}")
                    sys.exit(1)
        else:
            other_lines.append(('other', line))

    if not vertices:
        print("Error: No vertices found in OBJ")
        sys.exit(1)

    return vertices, other_lines


def calculate_bounding_box(vertices):
    """Calculate bounding box dimensions."""
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)

    width = max_x - min_x
    length = max_y - min_y
    height = max_z - min_z

    return width, length, height, (min_x, max_x, min_y, max_y, min_z, max_z)


def rotate_y(vertices, angle_degrees):
    """Rotate vertices around Y axis."""
    angle = math.radians(angle_degrees)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    rotated = []
    for x, y, z in vertices:
        new_x = x * cos_a + z * sin_a
        new_z = -x * sin_a + z * cos_a
        rotated.append((new_x, y, new_z))

    return rotated


def rotate_z(vertices, angle_degrees):
    """Rotate vertices around Z axis."""
    angle = math.radians(angle_degrees)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    rotated = []
    for x, y, z in vertices:
        new_x = x * cos_a - y * sin_a
        new_y = x * sin_a + y * cos_a
        rotated.append((new_x, new_y, z))

    return rotated


def rotate_x(vertices, angle_degrees):
    """Rotate vertices around X axis."""
    angle = math.radians(angle_degrees)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    rotated = []
    for x, y, z in vertices:
        new_y = y * cos_a - z * sin_a
        new_z = y * sin_a + z * cos_a
        rotated.append((x, new_y, new_z))

    return rotated


def scale_vertices(vertices, scale_factor):
    """Scale all vertices uniformly."""
    return [(x * scale_factor, y * scale_factor, z * scale_factor) for x, y, z in vertices]


def translate_vertices(vertices, tx=0, ty=0, tz=0):
    """Translate all vertices."""
    return [(x + tx, y + ty, z + tz) for x, y, z in vertices]


def write_obj_file(filename, vertices, other_lines):
    """Write OBJ file."""
    try:
        with open(filename, 'w') as f:
            for line_type, content in other_lines:
                if line_type == 'vertex':
                    x, y, z = vertices[content]
                    f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")
                else:
                    f.write(content + '\n')
    except Exception as e:
        print(f"Error: Failed to write output: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Transform OBJ 3D models')
    parser.add_argument('input_file', help='Input OBJ file')
    parser.add_argument('output_file', help='Output OBJ file')
    parser.add_argument('--scale', type=float, help='Uniform scale factor')
    parser.add_argument('--rotate-x', type=float, default=0, help='Rotation around X axis (degrees)')
    parser.add_argument('--rotate-y', type=float, default=0, help='Rotation around Y axis (degrees)')
    parser.add_argument('--rotate-z', type=float, default=0, help='Rotation around Z axis (degrees)')
    parser.add_argument('--translate-x', type=float, default=0, help='Translation along X axis')
    parser.add_argument('--translate-y', type=float, default=0, help='Translation along Y axis')
    parser.add_argument('--translate-z', type=float, default=0, help='Translation along Z axis')

    args = parser.parse_args()

    print(f"Reading {args.input_file}...")
    vertices, other_lines = read_obj_file(args.input_file)
    print(f"Found {len(vertices)} vertices")

    # Show original dimensions
    width, length, height, bbox = calculate_bounding_box(vertices)
    print(f"Original dimensions: width={width:.6f}, length={length:.6f}, height={height:.6f}")
    print(f"Original Z range: {bbox[4]:.6f} to {bbox[5]:.6f}")

    # Apply rotations first
    if args.rotate_x != 0:
        print(f"Rotating {args.rotate_x}° around X axis...")
        vertices = rotate_x(vertices, args.rotate_x)

    if args.rotate_y != 0:
        print(f"Rotating {args.rotate_y}° around Y axis...")
        vertices = rotate_y(vertices, args.rotate_y)

    if args.rotate_z != 0:
        print(f"Rotating {args.rotate_z}° around Z axis...")
        vertices = rotate_z(vertices, args.rotate_z)

    # Apply scaling
    if args.scale:
        print(f"Applying scale factor: {args.scale:.6f}")
        vertices = scale_vertices(vertices, args.scale)

    # Apply translation
    if args.translate_x != 0 or args.translate_y != 0 or args.translate_z != 0:
        print(f"Translating: X={args.translate_x:.6f}, Y={args.translate_y:.6f}, Z={args.translate_z:.6f}")
        vertices = translate_vertices(vertices, args.translate_x, args.translate_y, args.translate_z)

    # Show final dimensions
    width, length, height, bbox = calculate_bounding_box(vertices)
    print(f"Final dimensions: width={width:.6f}, length={length:.6f}, height={height:.6f}")
    print(f"Final Z range: {bbox[4]:.6f} to {bbox[5]:.6f}")

    print(f"Writing {args.output_file}...")
    write_obj_file(args.output_file, vertices, other_lines)
    print("Done!")


if __name__ == '__main__':
    main()
