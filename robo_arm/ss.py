# Main system flow

while True:

    # Step 1: Wait for voice command
    if listen_for_command():

        # Step 2: Detect biscuit using YOLO
        biscuit = detect_biscuit_count()

        if biscuit is not None:

            # Step 3: Move robotic arm to pick biscuit
            move_arm()

            # Step 4: Wait for user hand (MediaPipe + sensor)
            if hand_detected and distance_ok:
                
                # Step 5: Release biscuit
                release_biscuit()
                print("Biscuit delivered successfully")

            else:
                # Step 6: Fail-safe action
                return_to_plate()
                print("No hand detected - returned to plate")

        else:
            print("No biscuit detected")