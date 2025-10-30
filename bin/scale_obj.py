#!/usr/bin/env python3
"""
OBJ 3D Model Scaler
Scales OBJ files to specific dimensions while maintaining proportions.
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
    except Exception as e:
        print(f"Error: Failed to read input file: {e}")
        sys.exit(1)

    vertices = []
    other_lines = []

    for line in lines:
        line = line.strip()
        if line.startswith('v '):
            # Vertex line: "v x y z"
            parts = line.split()
            if len(parts) >= 4:
                try:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    vertices.append((x, y, z))
                    other_lines.append(('vertex', len(vertices) - 1))
                except ValueError:
                    print(f"Error: Invalid OBJ format - could not parse vertex: {line}")
                    sys.exit(1)
            else:
                print(f"Error: Invalid OBJ format - vertex line incomplete: {line}")
                sys.exit(1)
        else:
            # Keep all other lines as-is (vn, vt, f, comments, etc.)
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

    return width, length, height


def calculate_radius(vertices):
    """Calculate maximum distance from origin to any vertex (for wheels)."""
    max_radius = 0
    for x, y, z in vertices:
        radius = math.sqrt(x*x + y*y + z*z)
        if radius > max_radius:
            max_radius = radius
    return max_radius


def calculate_scale_factor(vertices, target_width=None, target_length=None, target_radius=None):
    """Calculate uniform scale factor based on target dimensions."""
    if target_radius is not None:
        # For wheels: scale based on radius
        current_radius = calculate_radius(vertices)
        print(f"Current radius: {current_radius:.6f}")
        scale_factor = target_radius / current_radius
    elif target_width is not None or target_length is not None:
        # For bodies: scale based on width and length
        current_width, current_length, current_height = calculate_bounding_box(vertices)
        print(f"Current dimensions: width={current_width:.6f}, length={current_length:.6f}, height={current_height:.6f}")

        scale_factors = []
        if target_width is not None:
            scale_x = target_width / current_width
            scale_factors.append(scale_x)
        if target_length is not None:
            scale_y = target_length / current_length
            scale_factors.append(scale_y)

        # Use average for uniform scaling
        scale_factor = sum(scale_factors) / len(scale_factors)
    else:
        print("Error: No target dimensions specified")
        sys.exit(1)

    if scale_factor <= 0:
        print("Error: Invalid scale factor")
        sys.exit(1)

    return scale_factor


def scale_vertices(vertices, scale_factor):
    """Scale all vertices by the given factor."""
    scaled_vertices = []
    for x, y, z in vertices:
        scaled_vertices.append((
            x * scale_factor,
            y * scale_factor,
            z * scale_factor
        ))
    return scaled_vertices


def write_obj_file(filename, vertices, other_lines):
    """Write scaled OBJ file."""
    try:
        with open(filename, 'w') as f:
            vertex_index = 0
            for line_type, content in other_lines:
                if line_type == 'vertex':
                    x, y, z = vertices[content]
                    f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")
                    vertex_index += 1
                else:
                    f.write(content + '\n')
    except Exception as e:
        print(f"Error: Failed to write output file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Scale OBJ 3D model files to specific dimensions')
    parser.add_argument('input_file', help='Input OBJ file')
    parser.add_argument('output_file', help='Output OBJ file')
    parser.add_argument('--target-length', type=float, help='Target length (Y-axis or longest dimension)')
    parser.add_argument('--target-width', type=float, help='Target width (X-axis)')
    parser.add_argument('--target-radius', type=float, help='Target radius (for wheels, from center to edge)')

    args = parser.parse_args()

    # Validate that at least one target dimension is provided
    if args.target_radius is None and args.target_width is None and args.target_length is None:
        print("Error: At least one target dimension must be specified")
        parser.print_help()
        sys.exit(1)

    print(f"Reading {args.input_file}...")
    vertices, other_lines = read_obj_file(args.input_file)
    print(f"Found {len(vertices)} vertices")

    # Calculate scale factor
    scale_factor = calculate_scale_factor(
        vertices,
        target_width=args.target_width,
        target_length=args.target_length,
        target_radius=args.target_radius
    )
    print(f"Scale factor: {scale_factor:.6f}")

    # Scale vertices
    scaled_vertices = scale_vertices(vertices, scale_factor)

    # Print final dimensions
    if args.target_radius is not None:
        final_radius = calculate_radius(scaled_vertices)
        print(f"Final radius: {final_radius:.6f}")
    else:
        final_width, final_length, final_height = calculate_bounding_box(scaled_vertices)
        print(f"Final dimensions: width={final_width:.6f}, length={final_length:.6f}, height={final_height:.6f}")

    # Write output file
    print(f"Writing {args.output_file}...")
    write_obj_file(args.output_file, scaled_vertices, other_lines)
    print("Done!")


if __name__ == '__main__':
    main()
