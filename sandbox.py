import csv
import random

# Number of points
num_points = 142

# Define the bounds
x_min, x_max = 1, 97
y_min, y_max = 1, 100
z_min, z_max = 1, 100

# Create a list of random coordinate points
points = {(random.randint(x_min, x_max), random.randint(y_min, y_max), random.randint(z_min, z_max)) for _ in range(num_points)}

# Define the CSV file name
csv_file = 'data.csv'

# Write the points to a CSV file
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(points)

print(f'{num_points} random coordinate points have been saved to {csv_file}')
