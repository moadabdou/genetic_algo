# -*- coding: utf-8 -*-
from manim import *
import operator
import json
# Added for the vertical line color
from manim import RED # <-- Added this import for the line color


class GeneralizedGeneticAlgorithmNoSqueeze(Scene):  # Renamed
    def construct(self):
        # --- Overall Configuration ---
        # (Same as before)
        gens = self.load_generation_data()
        if not gens or len(gens) < 1:
            self.add(Text("Error: Need at least one generation of data.").scale(0.5))
            return
        genome_font = "Monospace"
        genome_scale = 0.6
        fitness_scale = 0.45
        parent_scale = 0.8
        grid_rows = 4
        grid_cols = 5
        grid_h_buff = 1.2
        grid_v_buff = 1.0
        highlight_color = YELLOW
        fitness_color = BLUE
        pause_time = 0.3
        long_pause_time = 1.2
        fitness_delay = 1.5
        crossover_anim_time = 0.7
        mutation_anim_time = 0.5
        placement_anim_time = 0.6
        right_panel_width_percent = 0.25
        grid_width_percent = 1.0 - right_panel_width_percent - 0.05
        top_right_buff = 0.8
        # final_vertical_squeeze = 0.85 # No longer needed
        num_offspring_to_animate = 5
        # --- Start: Config for added features ---
        cut_line_color = RED
        cut_line_wait_time = 0.6
        cut_line_anim_time = 0.3
        final_result_scale = 1.1 # Optional scaling for the final best genome
        final_result_anim_time = 1.5
        # --- End: Config for added features ---

        # --- Initialization ---
        genome_mobs_on_screen = VGroup()
        fitness_mobs_on_screen = VGroup()
        title_on_screen = Text("")
        parents_at_top_right = VGroup()
        indicator_text = Text("")

        # --- Main Loop through Generations ---
        for gen_index in range(len(gens)):

            # --- 1. Data Setup ---
            current_gen_data = gens[gen_index]

            # --- 2. Display Grid & Title ---
            new_title = Text(f"Generation {gen_index}").scale(0.8).to_edge(UP)
            new_genome_texts = VGroup(
                *[
                    Text(item["value"], font=genome_font).scale(genome_scale)
                    for item in current_gen_data
                ]
            )
            new_genome_texts.arrange_in_grid(
                rows=grid_rows, cols=grid_cols, buff=(grid_h_buff, grid_v_buff)
            )
            new_genome_texts.set_width(self.camera.frame_width * grid_width_percent)
            new_genome_texts.to_edge(LEFT, buff=0.5)
            anims_in = [
                Write(new_title),
                FadeIn(new_genome_texts, shift=UP * 0.2, lag_ratio=0.05),
            ]
            anims_out = []
            if len(genome_mobs_on_screen) > 0:
                anims_out.append(FadeOut(genome_mobs_on_screen))
            if len(fitness_mobs_on_screen) > 0:
                anims_out.append(FadeOut(fitness_mobs_on_screen))
            if title_on_screen.text:
                anims_out.append(FadeOut(title_on_screen))
            if gen_index > 0 and indicator_text.text: # Fade out previous indicator if needed
                anims_out.append(FadeOut(indicator_text))
            self.play(*anims_out, *anims_in, run_time=1.5 if gen_index > 0 else 2.0)
            genome_mobs_on_screen = new_genome_texts
            title_on_screen = new_title
            fitness_mobs_on_screen = VGroup()
            indicator_text = Text("") # Reset indicator

            # --- 3. Show Fitness ---
            self.wait(fitness_delay)
            new_fitness_texts = VGroup()
            for i, item in enumerate(current_gen_data):
                fitness = Text(str(item["fitness"]), color=fitness_color).scale(
                    fitness_scale
                )
                if i < len(genome_mobs_on_screen):
                    fitness.next_to(genome_mobs_on_screen[i], UP, buff=0.25)
                    new_fitness_texts.add(fitness)
            self.play(
                AnimationGroup(
                    *[FadeIn(f, shift=UP * 0.1) for f in new_fitness_texts],
                    lag_ratio=0.07,
                    run_time=1.0,
                )
            )
            fitness_mobs_on_screen = new_fitness_texts
            self.wait(long_pause_time)

            # --- Check if last generation ---
            if gen_index == len(gens) - 1:
                # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                # --- START: FINAL RESULT DISPLAY LOGIC (Req 2) ---
                # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                if current_gen_data and genome_mobs_on_screen: # Check if there's data
                    # Find index of the best individual
                    best_index = max(
                        range(len(current_gen_data)),
                        key=lambda k: current_gen_data[k]["fitness"]
                    )
                    best_genome_mob = genome_mobs_on_screen[best_index]

                    # Create "Final Result" title
                    final_title = Text("Final Result").scale(0.9).to_edge(UP)

                    # Group everything to fade out EXCEPT the best genome
                    mobs_to_fade_final = VGroup(title_on_screen, fitness_mobs_on_screen)
                    for i, genome_mob in enumerate(genome_mobs_on_screen):
                        if i != best_index:
                            mobs_to_fade_final.add(genome_mob)
                    # Also fade out crossover indicator if it somehow exists
                    if indicator_text.text:
                        mobs_to_fade_final.add(indicator_text)

                    # Animation: Fade out others, move best to center, show final title
                    self.play(
                        FadeOut(mobs_to_fade_final, shift=DOWN*0.2),
                        best_genome_mob.animate.move_to(ORIGIN).scale(final_result_scale),
                        Write(final_title),
                        run_time=final_result_anim_time
                    )
                    # Update state to only contain the final elements (optional, as we break anyway)
                    genome_mobs_on_screen = VGroup(best_genome_mob)
                    fitness_mobs_on_screen = VGroup()
                    title_on_screen = final_title
                    indicator_text = Text("")

                else:
                     # Fallback: Just fade everything if last gen is empty
                     mobs_to_fade_final = VGroup(title_on_screen, fitness_mobs_on_screen, genome_mobs_on_screen, indicator_text)
                     self.play(FadeOut(mobs_to_fade_final))

                break # Exit the loop after handling the final generation
                # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                # --- END: FINAL RESULT DISPLAY LOGIC ---
                # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

            # --- 4. Select Elites ---
            # (Original code unchanged)
            sorted_indices = sorted(
                range(len(current_gen_data)),
                key=lambda k: current_gen_data[k]["fitness"],
                reverse=True,
            )
            if len(sorted_indices) < 2:
                print(f"Not enough elites in Gen {gen_index}")
                break
            top1_idx, top2_idx = sorted_indices[0], sorted_indices[1]
            # Need to ensure indices are valid for mobs on screen
            if top1_idx >= len(genome_mobs_on_screen) or top2_idx >= len(genome_mobs_on_screen) or \
               top1_idx >= len(fitness_mobs_on_screen) or top2_idx >= len(fitness_mobs_on_screen):
                 print(f"Error: Elite index out of bounds for mobs in Gen {gen_index}")
                 break # Added simple bounds check

            elite1_group = VGroup(
                genome_mobs_on_screen[top1_idx], fitness_mobs_on_screen[top1_idx]
            )
            elite2_group = VGroup(
                genome_mobs_on_screen[top2_idx], fitness_mobs_on_screen[top2_idx]
            )
            parent1_genome_mob = genome_mobs_on_screen[top1_idx]
            parent2_genome_mob = genome_mobs_on_screen[top2_idx]
            parent1_str = current_gen_data[top1_idx]["value"]
            parent2_str = current_gen_data[top2_idx]["value"]

            # --- 5. Highlight, Fade Others, Move Parents (REVISED LOGIC) ---
            # (Original code unchanged)
            # 5a. Highlight
            rect1 = SurroundingRectangle(elite1_group, color=highlight_color, buff=0.15)
            rect2 = SurroundingRectangle(elite2_group, color=highlight_color, buff=0.15)
            self.play(Create(rect1), Create(rect2))
            self.wait(long_pause_time * 0.8)
            # 5b. Fade out non-elites, title, all fitness, and highlights
            mobs_to_fade = VGroup(title_on_screen, fitness_mobs_on_screen, rect1, rect2)
            for i in range(len(genome_mobs_on_screen)):
                if i != top1_idx and i != top2_idx:
                    mobs_to_fade.add(genome_mobs_on_screen[i])
            self.play(FadeOut(mobs_to_fade, shift=DOWN * 0.3), run_time=1.0)
            # 5c. Move the remaining parent genomes to the top-right
            parents_target_layout = (
                VGroup(parent1_genome_mob.copy(), parent2_genome_mob.copy())
                .scale(parent_scale)
                .arrange(DOWN, buff=0.4)
                .to_edge(UP + RIGHT, buff=top_right_buff)
            )
            target_pos1 = parents_target_layout[0].get_center()
            target_pos2 = parents_target_layout[1].get_center()
            self.play(
                parent1_genome_mob.animate.move_to(target_pos1).scale(parent_scale),
                parent2_genome_mob.animate.move_to(target_pos2).scale(parent_scale),
                run_time=1.2,
            )
            parents_at_top_right = VGroup(parent1_genome_mob, parent2_genome_mob)
            genome_mobs_on_screen = VGroup()
            fitness_mobs_on_screen = VGroup()
            title_on_screen = Text("")
            self.wait(pause_time)

            # --- 6. Setup Indicator ---
            # (Original code unchanged)
            new_indicator = Text("Crossover", font_size=30).next_to(
                parents_at_top_right, DOWN, buff=0.5 # Moved below parents slightly
            )
            # Adjust positioning if too far right (simplified check)
            if new_indicator.get_right()[0] > self.camera.frame_width / 2 - 0.5:
                 new_indicator.next_to(parents_at_top_right, DOWN, buff=0.5).align_to(parents_at_top_right, RIGHT)

            self.play(Write(new_indicator))
            indicator_text = new_indicator
            self.wait(pause_time)

            # --- 7. Create Offspring ---
            next_gen_index = gen_index + 1
            # Add basic check if next gen exists in data
            if next_gen_index >= len(gens):
                 print(f"Error: No data found for generation {next_gen_index}. Stopping.")
                 self.play(FadeOut(parents_at_top_right), FadeOut(indicator_text)) # Clean up
                 break

            next_gen_data_full = gens[next_gen_index]
            next_gen_offspring_data = [
                d for d in next_gen_data_full if not d.get("parent", False)
            ]
            # Check if next gen has data for grid
            if not next_gen_data_full:
                print(f"Warning: Generation {next_gen_index} data is empty. Proceeding may cause errors.")
                # Optionally fade parents and stop, or continue carefully
                self.play(FadeOut(parents_at_top_right), FadeOut(indicator_text))
                continue # Skip offspring loop for this empty gen

            temp_grid_mobs = VGroup(
                *[
                    Square(stroke_width=0, fill_opacity=0).scale(genome_scale)
                    for _ in range(len(next_gen_data_full))
                ]
            )
             # Only arrange if mobs exist
            if len(temp_grid_mobs) > 0:
                temp_grid_mobs.arrange_in_grid(
                    rows=grid_rows, cols=grid_cols, buff=(grid_h_buff, grid_v_buff)
                )
                temp_grid_mobs.set_width(self.camera.frame_width * grid_width_percent)
                temp_grid_mobs.to_edge(LEFT, buff=0.5)
                next_grid_positions = [mob.get_center() for mob in temp_grid_mobs]
            else:
                 next_grid_positions = [] # No positions if grid is empty

            next_gen_genome_mobs_being_created = VGroup()
            mobs_to_fade_in_later = VGroup()

            for i, offspring in enumerate(next_gen_offspring_data):
                # Use .get() for safety in case keys are missing in json
                p = offspring.get("p")
                pre_value_str = offspring.get("pre_value", "")
                value_str = offspring.get("value", "")

                # Ensure target position index is valid
                target_index = i + 2 # Parents take [0], [1]
                if target_index >= len(next_grid_positions):
                     print(f"Warning: Not enough grid positions ({len(next_grid_positions)}) for offspring {i+1} (needs index {target_index}). Skipping.")
                     continue

                target_pos = next_grid_positions[target_index]

                # Check if p is valid before using it
                if p is None or not isinstance(p, int) or p < 0:
                     print(f"Warning: Invalid or missing 'p' for offspring {i}. Skipping animation.")
                     # Still create the final mob if value exists
                     if value_str:
                         final_genome_mob = (
                             Text(value_str, font=genome_font)
                             .scale(genome_scale)
                             .move_to(target_pos)
                         )
                         mobs_to_fade_in_later.add(final_genome_mob)
                         next_gen_genome_mobs_being_created.add(final_genome_mob)
                     continue # Skip the animation part for this offspring


                if i < num_offspring_to_animate:

                    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                    # --- START: ADDED VERTICAL LINE FOR CROSSOVER CUT (Req 1) ---
                    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                    cut_lines_to_show = VGroup()
                    # Calculate line for parent 1
                    # Check p is within string bounds and string/mob exists
                    if parent1_str and 0 < p < len(parent1_str) and parent1_genome_mob.get_width() > 1e-6:
                        p1_mob_ref = parent1_genome_mob # Use the mob currently in top-right
                        x_pos1 = p1_mob_ref.get_left()[0] + p1_mob_ref.get_width() * (p / len(parent1_str))
                        line1 = Line(
                            [x_pos1, p1_mob_ref.get_bottom()[1] - 0.05, 0], # Start slightly below
                            [x_pos1, p1_mob_ref.get_top()[1] + 0.05, 0], # End slightly above
                            color=cut_line_color, stroke_width=2.5
                        )
                        cut_lines_to_show.add(line1)

                    # Calculate line for parent 2
                    if parent2_str and 0 < p < len(parent2_str) and parent2_genome_mob.get_width() > 1e-6:
                        p2_mob_ref = parent2_genome_mob
                        x_pos2 = p2_mob_ref.get_left()[0] + p2_mob_ref.get_width() * (p / len(parent2_str))
                        line2 = Line(
                            [x_pos2, p2_mob_ref.get_bottom()[1] - 0.05, 0], # Start slightly below
                            [x_pos2, p2_mob_ref.get_top()[1] + 0.05, 0], # End slightly above
                            color=cut_line_color, stroke_width=2.5
                        )
                        cut_lines_to_show.add(line2)

                    # Animate the lines appearing and disappearing
                    if len(cut_lines_to_show) > 0:
                        self.play(Create(cut_lines_to_show), run_time=cut_line_anim_time)
                        self.wait(cut_line_wait_time)
                        self.play(FadeOut(cut_lines_to_show), run_time=cut_line_anim_time)
                        self.wait(pause_time * 0.5) # Small gap before crossover starts
                    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    # --- END: ADDED VERTICAL LINE FOR CROSSOVER CUT ---
                    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


                    # Crossover anim... (Original logic with slight correction for scale/position)
                    # Ensure p is within bounds for slicing safely
                    safe_p1 = min(p, len(parent1_str)) if parent1_str else 0
                    safe_p2 = min(p, len(parent2_str)) if parent2_str else 0

                    if i % 2 == 0:
                        part1_str = parent1_str[:safe_p1] if parent1_str else ""
                        part2_str = parent2_str[safe_p2:] if parent2_str else ""
                        p1_orig = parent1_genome_mob
                        p2_orig = parent2_genome_mob
                    else:
                        part1_str = parent2_str[:safe_p2] if parent2_str else ""
                        part2_str = parent1_str[safe_p1:] if parent1_str else ""
                        p1_orig = parent2_genome_mob
                        p2_orig = parent1_genome_mob

                    # --- Create part mobs AT the original parent positions initially ---
                    # Apply parent_scale correctly here for visual consistency
                    part1_mob = Text(part1_str, font=genome_font).scale(genome_scale * parent_scale) if part1_str else VGroup()
                    part2_mob = Text(part2_str, font=genome_font).scale(genome_scale * parent_scale) if part2_str else VGroup()

                    # Position them correctly at the start
                    if isinstance(part1_mob, Text):
                         part1_mob.move_to(p1_orig.get_center()).align_to(p1_orig, LEFT)
                    if isinstance(part2_mob, Text):
                         part2_mob.move_to(p2_orig.get_center()).align_to(p2_orig, RIGHT)

                    # Define merge position (relative to scaled parents)
                    merge_pos = parents_at_top_right.get_center() + DOWN * 1.5

                    # Create the target combined mob for alignment reference (also scaled)
                    pre_value_mob_target = (
                        Text(pre_value_str, font=genome_font)
                        .scale(genome_scale * parent_scale) # Apply parent scale
                        .move_to(merge_pos)
                    )

                    # Animate parts moving and aligning
                    anims_crossover = []
                    if isinstance(part1_mob, Text):
                        anims_crossover.append(part1_mob.animate.move_to(merge_pos).align_to(pre_value_mob_target, LEFT))
                    if isinstance(part2_mob, Text):
                        anims_crossover.append(part2_mob.animate.move_to(merge_pos).align_to(pre_value_mob_target, RIGHT))

                    if anims_crossover:
                        self.play(*anims_crossover, run_time=crossover_anim_time)
                    else:
                         self.wait(crossover_anim_time) # Wait even if no parts moved

                    self.wait(pause_time * 0.5)

                    # Create the actual pre_value_mob at the final location and add it
                    pre_value_mob = (
                        Text(pre_value_str, font=genome_font)
                        .scale(genome_scale * parent_scale) # Apply parent scale
                        .move_to(merge_pos)
                    )
                    self.add(pre_value_mob) # Add the combined mob
                    # Remove the individual parts safely
                    mobs_to_remove = VGroup(*[m for m in (part1_mob, part2_mob) if isinstance(m, Text)])
                    if len(mobs_to_remove) > 0:
                        self.remove(*mobs_to_remove)
                    self.wait(pause_time * 0.5)

                    mutation_indicator = Text("Mutation", font_size=30).next_to(
                        pre_value_mob, DOWN, buff=0.5 # Position below the mob *before* mutation
                    )
                    self.play(
                        Transform(indicator_text, mutation_indicator), run_time=0.3
                    )

                    # ... (mutation animation code) ...
                    value_mob = (
                        Text(value_str, font=genome_font)
                        .scale(genome_scale * parent_scale)
                        .move_to(pre_value_mob.get_center())
                    )
                    self.play(
                        Transform(pre_value_mob, value_mob), run_time=mutation_anim_time
                    )
                    final_genome_mob = pre_value_mob # This mob was transformed AFTER mutation
                    # NO scaling here yet

                    self.wait(pause_time * 0.5)

                    # --- Start of transforming back to Crossover indicator ---
                    crossover_indicator = Text("Crossover", font_size=30).next_to(
                        final_genome_mob, DOWN, buff=0.5 # Position below the mob *after* mutation (still scaled)
                    )
                    self.play(
                        Transform(indicator_text, crossover_indicator), run_time=0.3
                    )

                    # --- Scale back to normal genome size BEFORE placing in grid ---
                    final_genome_mob.scale(1 / parent_scale)
                    next_gen_genome_mobs_being_created.add(final_genome_mob) # Add it *after* scaling

                    # Placement anim... (Original logic)
                    self.play(
                        final_genome_mob.animate.move_to(target_pos), # Moves the now correctly-scaled mob
                        run_time=placement_anim_time,
                    )
                    self.wait(pause_time * 0.2)
                else:
                    # Store for FadeIn... (Original logic)
                    final_genome_mob = (
                        Text(value_str, font=genome_font)
                        .scale(genome_scale)
                        .move_to(target_pos)
                    )
                    mobs_to_fade_in_later.add(final_genome_mob)
                    next_gen_genome_mobs_being_created.add(final_genome_mob)

            # --- 8. Fade In Remaining Offspring ---
            # (Original code unchanged)
            if len(mobs_to_fade_in_later) > 0:
                self.play(FadeIn(mobs_to_fade_in_later, lag_ratio=0.05, run_time=1.0))
            self.wait(pause_time)

            # --- 9. Place Parents into Next Gen Grid ---
            # (Original code unchanged, including potential issue if grid is too small)
            target_scale_factor = 1 / parent_scale
            parents_placed_anims = []
            parents_added_to_next_gen = VGroup()
            if len(next_grid_positions) >= 1:
                 parent1_target_pos = next_grid_positions[0]
                 parents_placed_anims.append(parent1_genome_mob.animate.move_to(parent1_target_pos).scale(target_scale_factor))
                 parents_added_to_next_gen.add(parent1_genome_mob)
            if len(next_grid_positions) >= 2:
                 parent2_target_pos = next_grid_positions[1]
                 parents_placed_anims.append(parent2_genome_mob.animate.move_to(parent2_target_pos).scale(target_scale_factor))
                 parents_added_to_next_gen.add(parent2_genome_mob)

            # Determine parents to fade out if not placed
            parents_to_fade = VGroup()
            if parent1_genome_mob not in parents_added_to_next_gen:
                 parents_to_fade.add(parent1_genome_mob)
            if parent2_genome_mob not in parents_added_to_next_gen:
                 parents_to_fade.add(parent2_genome_mob)

            # Play placement and fade animations
            if parents_placed_anims:
                 self.play(*parents_placed_anims, run_time=1.0)
            if len(parents_to_fade) > 0:
                 self.play(FadeOut(parents_to_fade))

            # Add placed parents to the group for the next generation screen state
            next_gen_genome_mobs_being_created.add(*parents_added_to_next_gen)


            # --- 10. Update State for Next Iteration ---
            # (Original code unchanged - simply assigns the created mobs)
            # Potential issue: Order might not match grid if parents faded.
            # For strict adherence to "don't change", leaving this as is.
            genome_mobs_on_screen = next_gen_genome_mobs_being_created
            parents_at_top_right = VGroup() # Clear parents from top right


            # --- 11. Transition Pause ---
            # (Original code unchanged)
            self.wait(long_pause_time * 0.5)

        # --- End of Loop ---

        # --- Final Step ---
        # (Original code unchanged, indicator fade out might be redundant now)
        # Fade out the indicator text only if it exists AND wasn't handled by the final screen logic
        if indicator_text.text and title_on_screen.text != "Final Result":
             self.play(FadeOut(indicator_text))


        self.wait(long_pause_time * 2)  # Final hold

    # --- Helper to load data ---
    # (Original code unchanged)
    def load_generation_data(self):
        # Basic error handling added for file IO, but not data validation
        try:
            with open("gens.json", "r") as f:
                gens_data = json.load(f)
        except FileNotFoundError:
            print("Error: gens.json not found.")
            self.add(Text("Error: gens.json not found.", color=RED).scale(0.6).to_edge(DOWN)) # Show error on screen
            return []
        except json.JSONDecodeError:
            print("Error: Could not decode JSON from gens.json.")
            self.add(Text("Error: Invalid JSON in gens.json.", color=RED).scale(0.6).to_edge(DOWN)) # Show error on screen
            return []
        
        for  i,g in enumerate(gens_data):
            if (len(g) != 20):
                raise BaseException("gen  len not supported [must be 20] given : " +str(len(g))+" at gen "+str(i))

        # Limit to 2 generations as per original code
        return gens_data