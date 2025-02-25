import math


class Reward:
    def __init__(self, verbose=False):
        self.first_racingpoint_index = 0
        self.verbose = verbose

    def reward_function(self, params):

        # Import package (needed for heading)
        # import math

        ################## HELPER FUNCTIONS ###################

        def dist_2_points(x1, x2, y1, y2):
            return abs(abs(x1-x2)**2 + abs(y1-y2)**2)**0.5

        def closest_2_racing_points_index(racing_coords, car_coords):

            # Calculate all distances to racing points
            distances = []
            for i in range(len(racing_coords)):
                distance = dist_2_points(x1=racing_coords[i][0], x2=car_coords[0],
                                         y1=racing_coords[i][1], y2=car_coords[1])
                distances.append(distance)

            # Get index of the closest racing point
            closest_index = distances.index(min(distances))

            # Get index of the second closest racing point
            distances_no_closest = distances.copy()
            distances_no_closest[closest_index] = 999
            second_closest_index = distances_no_closest.index(
                min(distances_no_closest))

            return [closest_index, second_closest_index]

        def dist_to_racing_line(closest_coords, second_closest_coords, car_coords):
            
            # Calculate the distances between 2 closest racing points
            a = abs(dist_2_points(x1=closest_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=closest_coords[1],
                                  y2=second_closest_coords[1]))

            # Distances between car and closest and second closest racing point
            b = abs(dist_2_points(x1=car_coords[0],
                                  x2=closest_coords[0],
                                  y1=car_coords[1],
                                  y2=closest_coords[1]))
            c = abs(dist_2_points(x1=car_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=car_coords[1],
                                  y2=second_closest_coords[1]))

            # Calculate distance between car and racing line (goes through 2 closest racing points)
            # try-except in case a=0 (rare bug in DeepRacer)
            try:
                distance = abs(-(a**4) + 2*(a**2)*(b**2) + 2*(a**2)*(c**2) -
                               (b**4) + 2*(b**2)*(c**2) - (c**4))**0.5 / (2*a)
            except:
                distance = b

            return distance

        # Calculate which one of the closest racing points is the next one and which one the previous one
        def next_prev_racing_point(closest_coords, second_closest_coords, car_coords, heading):

            # Virtually set the car more into the heading direction
            heading_vector = [math.cos(math.radians(
                heading)), math.sin(math.radians(heading))]
            new_car_coords = [car_coords[0]+heading_vector[0],
                              car_coords[1]+heading_vector[1]]

            # Calculate distance from new car coords to 2 closest racing points
            distance_closest_coords_new = dist_2_points(x1=new_car_coords[0],
                                                        x2=closest_coords[0],
                                                        y1=new_car_coords[1],
                                                        y2=closest_coords[1])
            distance_second_closest_coords_new = dist_2_points(x1=new_car_coords[0],
                                                               x2=second_closest_coords[0],
                                                               y1=new_car_coords[1],
                                                               y2=second_closest_coords[1])

            if distance_closest_coords_new <= distance_second_closest_coords_new:
                next_point_coords = closest_coords
                prev_point_coords = second_closest_coords
            else:
                next_point_coords = second_closest_coords
                prev_point_coords = closest_coords

            return [next_point_coords, prev_point_coords]

        def racing_direction_diff(closest_coords, second_closest_coords, car_coords, heading):

            # Calculate the direction of the center line based on the closest waypoints
            next_point, prev_point = next_prev_racing_point(closest_coords,
                                                            second_closest_coords,
                                                            car_coords,
                                                            heading)

            # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
            track_direction = math.atan2(
                next_point[1] - prev_point[1], next_point[0] - prev_point[0])

            # Convert to degree
            track_direction = math.degrees(track_direction)

            # Calculate the difference between the track direction and the heading direction of the car
            direction_diff = abs(track_direction - heading)
            if direction_diff > 180:
                direction_diff = 360 - direction_diff

            return direction_diff

        # Gives back indexes that lie between start and end index of a cyclical list 
        # (start index is included, end index is not)
        def indexes_cyclical(start, end, array_len):
            if start is None:
                raise ValueError("start cannot be None")

            if end < start:
                end += array_len

            return [index % array_len for index in range(start, end)]

        # Calculate how long car would take for entire lap, if it continued like it did until now
        def projected_time(first_index, closest_index, step_count, times_list):

            # Calculate how much time has passed since start
            current_actual_time = (step_count-1) / 15

            # Calculate which indexes were already passed
            indexes_traveled = indexes_cyclical(first_index, closest_index, len(times_list))

            # Calculate how much time should have passed if car would have followed optimals
            current_expected_time = sum([times_list[i] for i in indexes_traveled])

            # Calculate how long one entire lap takes if car follows optimals
            total_expected_time = sum(times_list)

            # Calculate how long car would take for entire lap, if it continued like it did until now
            try:
                projected_time = (current_actual_time/current_expected_time) * total_expected_time
            except:
                projected_time = 9999

            return projected_time

        #################### RACING LINE ######################

        # Optimal racing line for the Spain track
        # Each row: [x,y,speed,timeFromPreviousPoint]
        racing_track = [[-1.19381, -1.63423, 3.38998, 0.06667],
                        [-1.40393, -1.58557, 3.38998, 0.06362],
                        [-1.60374, -1.52396, 3.38998, 0.06168],
                        [-1.7951, -1.4475, 3.38998, 0.06079],
                        [-1.9792, -1.35349, 3.38998, 0.06098],
                        [-2.15641, -1.23805, 3.38998, 0.06239],
                        [-2.32557, -1.0958, 3.42618, 0.06451],
                        [-2.48561, -0.92693, 3.23556, 0.07191],
                        [-2.63289, -0.72819, 3.07196, 0.08052],
                        [-2.76153, -0.49656, 2.93085, 0.0904],
                        [-2.86298, -0.23024, 2.79721, 0.10188],
                        [-2.92581, 0.06809, 2.56464, 0.11888],
                        [-2.93872, 0.34846, 2.56464, 0.10944],
                        [-2.90693, 0.60818, 2.56464, 0.10203],
                        [-2.83449, 0.84516, 2.56464, 0.09662],
                        [-2.72414, 1.05701, 2.56464, 0.09314],
                        [-2.57727, 1.24, 2.56464, 0.09149],
                        [-2.39209, 1.3846, 2.6866, 0.08745],
                        [-2.17704, 1.48853, 2.82239, 0.08463],
                        [-1.94003, 1.54992, 2.9781, 0.08221],
                        [-1.68882, 1.56804, 3.15914, 0.07972],
                        [-1.43074, 1.54374, 3.37554, 0.07679],
                        [-1.17212, 1.47955, 3.63963, 0.07321],
                        [-0.91777, 1.37937, 3.97637, 0.06875],
                        [-0.67076, 1.24811, 4.0, 0.06993],
                        [-0.43248, 1.09106, 4.0, 0.07134],
                        [-0.20283, 0.9138, 4.0, 0.07253],
                        [0.03588, 0.74949, 4.0, 0.07245],
                        [0.2813, 0.59932, 4.0, 0.07193],
                        [0.53317, 0.46303, 3.93478, 0.07278],
                        [0.79132, 0.34046, 3.14852, 0.09076],
                        [1.05562, 0.23162, 2.69736, 0.10597],
                        [1.32604, 0.13665, 2.39429, 0.11971],
                        [1.60257, 0.05582, 2.17359, 0.13255],
                        [1.87019, -0.00717, 2.0, 0.13746],
                        [2.11422, -0.09426, 2.0, 0.12955],
                        [2.32407, -0.2105, 2.0, 0.11995],
                        [2.49194, -0.35521, 2.0, 0.11082],
                        [2.61172, -0.52413, 2.0, 0.10354],
                        [2.67742, -0.71065, 2.0, 0.09888],
                        [2.68132, -0.90518, 2.07303, 0.09386],
                        [2.62887, -1.09629, 2.07303, 0.0956],
                        [2.51507, -1.27164, 2.42285, 0.08628],
                        [2.35287, -1.42472, 2.64836, 0.08421],
                        [2.14656, -1.54897, 2.94341, 0.08182],
                        [1.90203, -1.63947, 3.36306, 0.07753],
                        [1.62769, -1.69499, 4.0, 0.06997],
                        [1.33365, -1.71995, 4.0, 0.07377],
                        [1.02938, -1.72495, 4.0, 0.07608],
                        [0.7216, -1.7247, 4.0, 0.07695],
                        [0.41382, -1.72485, 4.0, 0.07695],
                        [0.10603, -1.72531, 4.0, 0.07695],
                        [-0.19362, -1.72315, 4.0, 0.07491],
                        [-0.47375, -1.71468, 4.0, 0.07007],
                        [-0.732, -1.69778, 3.81209, 0.06789],
                        [-0.97087, -1.67129, 3.58601, 0.06702]]

        ################## INPUT PARAMETERS ###################

        # Read all input parameters
        all_wheels_on_track = params['all_wheels_on_track']
        x = params['x']
        y = params['y']
        distance_from_center = params['distance_from_center']
        is_left_of_center = params['is_left_of_center']
        heading = params['heading']
        progress = params['progress']
        steps = params['steps']
        speed = params['speed']
        steering_angle = params['steering_angle']
        track_width = params['track_width']
        waypoints = params['waypoints']
        closest_waypoints = params['closest_waypoints']
        is_offtrack = params['is_offtrack']

        ############### OPTIMAL X,Y,SPEED,TIME ################

        # Get closest indexes for racing line (and distances to all points on racing line)
        closest_index, second_closest_index = closest_2_racing_points_index(
            racing_track, [x, y])

        # Get optimal [x, y, speed, time] for closest and second closest index
        optimals = racing_track[closest_index]
        optimals_second = racing_track[second_closest_index]

        # Save first racingpoint of episode for later
        if self.verbose == True:
            self.first_racingpoint_index = 0 # this is just for testing purposes
        if steps == 1:
            self.first_racingpoint_index = closest_index

        ################ REWARD AND PUNISHMENT ################

        ## Define the default reward ##
        reward = 1

        ## Reward if car goes close to optimal racing line ##
        DISTANCE_MULTIPLE = 1
        dist = dist_to_racing_line(optimals[0:2], optimals_second[0:2], [x, y])
        distance_reward = max(1e-3, 1 - (dist/(track_width*0.5)))
        reward += distance_reward * DISTANCE_MULTIPLE

        ## Reward if speed is close to optimal speed ##
        SPEED_DIFF_NO_REWARD = 1
        SPEED_MULTIPLE = 2
        speed_diff = abs(optimals[2]-speed)
        if speed_diff <= SPEED_DIFF_NO_REWARD:
            # we use quadratic punishment (not linear) bc we're not as confident with the optimal speed
            # so, we do not punish small deviations from optimal speed
            speed_reward = (1 - (speed_diff/(SPEED_DIFF_NO_REWARD))**2)**2
        else:
            speed_reward = 0
        reward += speed_reward * SPEED_MULTIPLE

        # Reward if less steps
        REWARD_PER_STEP_FOR_FASTEST_TIME = 1 
        STANDARD_TIME = 37
        FASTEST_TIME = 27
        times_list = [row[3] for row in racing_track]
        projected_time = projected_time(self.first_racingpoint_index, closest_index, steps, times_list)
        try:
            steps_prediction = projected_time * 15 + 1
            reward_prediction = max(1e-3, (-REWARD_PER_STEP_FOR_FASTEST_TIME*(FASTEST_TIME) /
                                           (STANDARD_TIME-FASTEST_TIME))*(steps_prediction-(STANDARD_TIME*15+1)))
            steps_reward = min(REWARD_PER_STEP_FOR_FASTEST_TIME, reward_prediction / steps_prediction)
        except:
            steps_reward = 0
        reward += steps_reward

        # Zero reward if obviously wrong direction (e.g. spin)
        direction_diff = racing_direction_diff(
            optimals[0:2], optimals_second[0:2], [x, y], heading)
        if direction_diff > 30:
            reward = 1e-3
            
        # Zero reward of obviously too slow
        speed_diff_zero = optimals[2]-speed
        if speed_diff_zero > 0.5:
            reward = 1e-3
            
        ## Incentive for finishing the lap in less steps ##
        REWARD_FOR_FASTEST_TIME = 1500 # should be adapted to track length and other rewards
        STANDARD_TIME = 37  # seconds (time that is easily done by model)
        FASTEST_TIME = 27  # seconds (best time of 1st place on the track)
        if progress == 100:
            finish_reward = max(1e-3, (-REWARD_FOR_FASTEST_TIME /
                      (15*(STANDARD_TIME-FASTEST_TIME)))*(steps-STANDARD_TIME*15))
        else:
            finish_reward = 0
        reward += finish_reward
        
        ## Zero reward if off track ##
        if all_wheels_on_track == False:
            reward = 1e-3

        ####################### VERBOSE #######################
        
        if self.verbose == True:
            print("Closest index: %i" % closest_index)
            print("Distance to racing line: %f" % dist)
            print("=== Distance reward (w/out multiple): %f ===" % (distance_reward))
            print("Optimal speed: %f" % optimals[2])
            print("Speed difference: %f" % speed_diff)
            print("=== Speed reward (w/out multiple): %f ===" % speed_reward)
            print("Direction difference: %f" % direction_diff)
            print("Predicted time: %f" % projected_time)
            print("=== Steps reward: %f ===" % steps_reward)
            print("=== Finish reward: %f ===" % finish_reward)
            
        #################### RETURN REWARD ####################
        
        # Always return a float value
        return float(reward)


reward_object = Reward() # add parameter verbose=True to get noisy output for testing


def reward_function(params):
    return reward_object.reward_function(params)