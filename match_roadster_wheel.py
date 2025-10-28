#!/usr/bin/env python3
"""
Transform mcqueenchar.obj to EXACTLY match roadster wheel bounds
"""

# Read roadster wheel to get target bounds
target_vertices = []
with open('static/media/roadster_wheel_02.bbc40837.obj.backup', 'r') as f:
    for line in f:
        if line.startswith('v '):
            parts = line.split()
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            target_vertices.append((x, y, z))

target_xs = [v[0] for v in target_vertices]
target_ys = [v[1] for v in target_vertices]
target_zs = [v[2] for v in target_vertices]

target_min_x, target_max_x = min(target_xs), max(target_xs)
target_min_y, target_max_y = min(target_ys), max(target_ys)
target_min_z, target_max_z = min(target_zs), max(target_zs)

print("Target (Roadster wheel) bounds:")
print(f"  X: {target_min_x:.6f} to {target_max_x:.6f}")
print(f"  Y: {target_min_y:.6f} to {target_max_y:.6f}")
print(f"  Z: {target_min_z:.6f} to {target_max_z:.6f}")

# Read mcqueenchar
source_vertices = []
other_lines = []
with open('mcqueenchar.obj', 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('v '):
            parts = line.split()
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            source_vertices.append((x, y, z))
            other_lines.append(('vertex', len(source_vertices) - 1))
        else:
            other_lines.append(('other', line))

print(f"\nSource (mcqueenchar) vertices: {len(source_vertices)}")

# Transform vertices
# Axis mapping: X→Z, Y→X, Z→Y (to reorient from X-flat to Z-flat)
transformed = []
for x, y, z in source_vertices:
    new_x = y  # Y becomes X
    new_y = z  # Z becomes Y
    new_z = x  # X becomes Z
    transformed.append((new_x, new_y, new_z))

# Get bounds after reorientation
xs = [v[0] for v in transformed]
ys = [v[1] for v in transformed]
zs = [v[2] for v in transformed]

source_min_x, source_max_x = min(xs), max(xs)
source_min_y, source_max_y = min(ys), max(ys)
source_min_z, source_max_z = min(zs), max(zs)

print(f"\nAfter reorientation:")
print(f"  X: {source_min_x:.6f} to {source_max_x:.6f}")
print(f"  Y: {source_min_y:.6f} to {source_max_y:.6f}")
print(f"  Z: {source_min_z:.6f} to {source_max_z:.6f}")

# Calculate scale factors for each axis
scale_x = (target_max_x - target_min_x) / (source_max_x - source_min_x)
scale_y = (target_max_y - target_min_y) / (source_max_y - source_min_y)
scale_z = (target_max_z - target_min_z) / (source_max_z - source_min_z)

# Use uniform scale for circular dimensions (X and Y)
uniform_scale = (scale_x + scale_y) / 2

print(f"\nScale factors:")
print(f"  X: {scale_x:.6f}")
print(f"  Y: {scale_y:.6f}")
print(f"  Z: {scale_z:.6f}")
print(f"  Using uniform: {uniform_scale:.6f}")

# Scale vertices
scaled = []
for x, y, z in transformed:
    new_x = x * uniform_scale
    new_y = y * uniform_scale
    new_z = z * uniform_scale
    scaled.append((new_x, new_y, new_z))

# Get bounds after scaling
xs = [v[0] for v in scaled]
ys = [v[1] for v in scaled]
zs = [v[2] for v in scaled]

scaled_min_x, scaled_max_x = min(xs), max(xs)
scaled_min_y, scaled_max_y = min(ys), max(ys)
scaled_min_z, scaled_max_z = min(zs), max(zs)

print(f"\nAfter scaling:")
print(f"  X: {scaled_min_x:.6f} to {scaled_max_x:.6f}")
print(f"  Y: {scaled_min_y:.6f} to {scaled_max_y:.6f}")
print(f"  Z: {scaled_min_z:.6f} to {scaled_max_z:.6f}")

# Calculate translation to match target center
scaled_center_x = (scaled_min_x + scaled_max_x) / 2
scaled_center_y = (scaled_min_y + scaled_max_y) / 2
scaled_center_z = (scaled_min_z + scaled_max_z) / 2

target_center_x = (target_min_x + target_max_x) / 2
target_center_y = (target_min_y + target_max_y) / 2
target_center_z = (target_min_z + target_max_z) / 2

translate_x = target_center_x - scaled_center_x
translate_y = target_center_y - scaled_center_y
translate_z = target_center_z - scaled_center_z

print(f"\nTranslation:")
print(f"  X: {translate_x:.6f}")
print(f"  Y: {translate_y:.6f}")
print(f"  Z: {translate_z:.6f}")

# Apply translation
final = []
for x, y, z in scaled:
    new_x = x + translate_x
    new_y = y + translate_y
    new_z = z + translate_z
    final.append((new_x, new_y, new_z))

# Verify final bounds
xs = [v[0] for v in final]
ys = [v[1] for v in final]
zs = [v[2] for v in final]

final_min_x, final_max_x = min(xs), max(xs)
final_min_y, final_max_y = min(ys), max(ys)
final_min_z, final_max_z = min(zs), max(zs)

print(f"\nFinal result:")
print(f"  X: {final_min_x:.6f} to {final_max_x:.6f}")
print(f"  Y: {final_min_y:.6f} to {final_max_y:.6f}")
print(f"  Z: {final_min_z:.6f} to {final_max_z:.6f}")

print(f"\nTarget match:")
print(f"  X: {'✓' if abs(final_min_x - target_min_x) < 0.01 and abs(final_max_x - target_max_x) < 0.01 else '✗'}")
print(f"  Y: {'✓' if abs(final_min_y - target_min_y) < 0.01 and abs(final_max_y - target_max_y) < 0.01 else '✗'}")
print(f"  Z: {'✓' if abs(final_min_z - target_min_z) < 0.1 and abs(final_max_z - target_max_z) < 0.1 else '✗'}")

# Write output
with open('mcqueenchar_matched.obj', 'w') as f:
    for line_type, content in other_lines:
        if line_type == 'vertex':
            x, y, z = final[content]
            f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")
        else:
            f.write(content + '\n')

print("\nWrote: mcqueenchar_matched.obj")
