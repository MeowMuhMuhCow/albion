# Funktionskatalog

Was jede Quelldatei im Spiel macht und was jede Funktion darin tut. Die Modulbeschreibungen sind neu geschrieben.
Die Funktionsbeschreibungen stammen aus den Funktionsköpfen im Quelltext: fast alle sind Originalköpfe von Blue Byte
(englisch, in der Bibliothek PCLIB32 teils deutsch). Köpfe, die erst bei der Rekonstruktion geschrieben wurden, sind mit **R** markiert.

| Kennzahl | Wert |
|---|---|
| Quelldateien | 135 |
| Funktionen | 2343 |
| davon mit Originalkopf | 2089 |
| davon mit Kopf aus der Rekonstruktion (R) | 177 |
| davon nur mit kurzem Kommentar (Setup-Programm) | 77 |

Zeilennummern beziehen sich auf die Datei in `src/`. Funktionen in `#if FALSE`-Blöcken werden nicht übersetzt und sind mit *(aus)* markiert.

## Inhalt

- [Kampf](#kampf) (6 Dateien)
- [Kampfmagie](#kampfmagie) (6 Dateien)
- [Karten](#karten) (12 Dateien)
- [Textsystem](#textsystem) (7 Dateien)
- [Oberfläche](#oberfläche) (15 Dateien)
- [Hilfsmodule](#hilfsmodule) (10 Dateien)
- [Spiel](#spiel) (38 Dateien)
- [Blue-Byte-Bibliothek PCLIB32](#blue-byte-bibliothek-pclib32) (18 Dateien)
- [Setup-Programm (nicht Teil von MAIN.EXE)](#setup-programm-nicht-teil-von-mainexe) (14 Dateien)
- [Weitere Quellen (nicht Teil von MAIN.EXE)](#weitere-quellen-nicht-teil-von-mainexe) (1 Dateien)
- [Werkzeuge der Entwickler (nicht Teil von MAIN.EXE)](#werkzeuge-der-entwickler-nicht-teil-von-mainexe) (8 Dateien)

## Kampf

### COMACTS.C

`src/ALBION/SRC/COMBAT/COMACTS.C` – Kampfaktionen: Bewegen, Nahkampf, Fernkampf, Schaden berechnen, Munition.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Move_combat_action` | Move combat action handler. | 103 |
| `Close_range_combat_action` | Close-range attack combat action handler. | 256 |
| `Do_close_range_attack` | Do close-range attack action. | 328 |
| `Calculate_afflicted_damage` | Calculate the damage afflicted by an attack. | 582 |
| `Long_range_combat_action` | Long-range attack combat action handler. | 650 |
| `Do_long_range_attack` | Do long-range attack action. | 720 |
| `Remove_ammo_and_reload` | Remove the current weapon's ammunition and try to reload. | 983 |
| `Search_and_remove_ammo` | Search and remove ammo from a character. | 1055 |
| `Flee_combat_action` | Flee combat action handler. | 1134 |
| `Cast_spell_combat_action` | Cast spell combat action handler. | 1200 |
| `Use_magic_object_combat_action` | Use magic object combat action handler. | 1300 |
| `Break_combat_items` | Try to break items used in combat. | 1376 |

### COMBAT.C

`src/ALBION/SRC/COMBAT/COMBAT.C` – Kampfrahmen: Kampf betreten und verlassen, Runden, Teilnehmer, Anzeige des Kampfes.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Enter_Combat` | Enter the combat screen. | 196 |
| `Combat_ModInit` | Initialize Combat module. | 365 |
| `Combat_ModExit` | Exit Combat module. | 517 |
| `Init_Combat_display` | Initialize Combat display. | 572 |
| `Exit_Combat_display` | Exit Combat display. | 620 |
| `Update_Combat_display` | Update Combat display. | 649 |
| `Combat_round` | Execute a round of combat. | 744 |
| `End_of_battle` | Determine if the battle has ended. | 910 |
| `Update_control_status` | Update the control status of all current combat participants. | 973 |
| `Remove_participant` | Remove a participant from combat. | 1092 |
| `Reset_combat_actions` | Reset the actions of all participants. | 1140 |
| `Handle_combat_environment_events` | Handle_combat_environment_events | 1182 |
| `Handle_combat_temporary_effects_event` | Handle_combat_temporary_effects_event | 1234 |
| `Add_temporary_effect` | Add a temporary effect to a combat participant. | 1338 |
| `Remove_temporary_effect` | Remove a temporary effect from a combat participant. | 1459 |
| `Remove_all_temporary_effects` | Remove all temporary effects from a combat participant. | 1558 |
| `Determine_monster_actions` | Determine monster actions. | 1588 |
| `Determine_uncontrollable_actions` | Determine uncontrollable participants' actions. | 1626 |
| `Select_uncontrollable_action` | Select an action for an uncontrollable participant. | 1680 |
| `Select_panicked_action` | Select an action for a panicked participant. | 1730 |
| `Select_crazy_action` | Select an action for a crazy participant. | 1887 |
| `Try_crazy_move` | Try to move a crazy participant. | 1935 |
| `Try_crazy_attack` | Try to let a crazy participant attack. | 1980 |
| `Create_sorted_combat_event_list` | Create a sorted list with all combat events. | 2079 |
| `Swap_combat_events` | Swap two combat events (for sorting). | 2172 |
| `Compare_combat_events` | Compare two combat events (for sorting). | 2205 |
| `Init_party_combat_data` | Init party combat data. | 2229 |
| `Exit_party_combat_data` | Exit party combat data. | 2306 |
| `Init_monster_combat_data` | Init monster combat data. | 2341 |
| `Exit_monster_combat_data` | Exit monster combat data. | 2518 |
| `Clone_monster_data` | Create clone of monster character data | 2560 |
| `Do_monster_appear_animations` | Show each monster's appear animation. | 2660 |
| `Set_combat_animation` | Set a participant's animation. | 2704 |
| `Has_combat_animation` | Check if a participant has a certain combat animation. | 2742 |
| `Get_combat_animation_length` | Get the length of a participant's combat animation. | 2783 |
| `Wait_4_combat_animation` | Wait for the end of a combat animation. | 2830 |
| `Wait_4_half_combat_animation` | Wait for until the first half of a combat animation has passed. | 2862 |
| `Update_combat_animations` | Update combat animations. | 2930 |
| `Update_monster_animation` | Update a monster's animation. | 2970 |
| `Get_close_range_targets` | Make bitlist of close-range attack targets. | 3099 |
| `Do_close_range_targets` | Make bitlist of close-range attack targets. | 3130 |
| `Get_long_range_targets` | Make bitlist of long-range attack targets. | 3197 |
| `Get_nr_moves` | Calculate number of moves of a combat participant. | 3245 |
| `Get_movement_range` | Determine movement range. | 3270 |
| `Get_occupied_move_targets` | Make bitlist of occupied movement targets. | 3406 |
| `Get_party_targets` | Make bitlist of party member targets. | 3465 |
| `Get_monster_targets` | Make bitlist of monster targets. | 3513 |
| `Print_combat_message` | Print a combat message. | 3573 |
| `Print_part_message` | Print a combat message referring to a combat participant. | 3611 |
| `Do_combat_damage` | Do damage to a combat participant. | 3653 |
| `Kill_participant` | Kill a combat participant. | 3801 |
| `Destroy_participant` | Destroy a combat participant. | 3861 |
| `Install_trap` | Install a trap. | 3912 |
| `Remove_trap` | Remove a trap. | 3946 |
| `Is_trap` | Is there a trap here? | 3989 |
| `Count_remaining_monsters` | Count the monsters remaining in combat. | 4027 |
| `Count_remaining_party_members` | Count the party members remaining in combat. | 4073 |
| `Count_fled_party_members` | Count the party members that have fled. | 4124 |

### COMOBS.C

`src/ALBION/SRC/COMBAT/COMOBS.C` – Kampfobjekte (COMOBs): alles, was im Kampf gezeichnet wird, samt Verhalten (Bewegung, Animation).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_COMOB_system` | Initialize COMbat OBject system. | 111 |
| `Exit_COMOB_system` | Exit COMbat OBject system. | 220 |
| `Add_COMOB` | Add a COMOB to the current list. | 293 |
| `Delete_COMOB` | Remove a COMOB from the current list. | 361 |
| `Duplicate_COMOB` | Duplicate a COMOB. | 454 |
| `Hide_COMOB` | Hide a COMOB. | 502 |
| `Show_COMOB` | Show a COMOB. | 531 |
| `Add_COMOB_behaviour` | Add a COMOB behaviour to the current list. | 565 |
| `Delete_COMOB_behaviour` | Remove a COMOB behaviour from the current list. | 637 |
| `Draw_combat_screen` | Draw combat screen main 3D window. | 669 |
| `Swap_COMOBs` | Swap two COMOBs (for sorting). | 790 |
| `Compare_COMOBs` | Compare two COMOBs (for sorting). | 820 |
| `Update_COMOBs` | Update all COMOBs. | 845 |
| `Clean_up_COMOB_list` | Remove all deleted COMOBs, activate new COMOBs, clean up list, and count remaining COMOBs. | 958 |
| `Draw_COMOB` | Draw a COMOB. | 1021 |
| `Get_COMOB_source_size` | Get size of COMOB source graphics. | 1339 |
| `Get_COMOB_graphics_ptr` | Get pointer to COMOB source graphics. | 1406 |
| `Get_COMOB_rectangle` | Get the 3D rectangle that covers a COMOB. | 1464 |
| `Animate_all_COMOBs` | Animate all COMOBs. | 1526 |
| `Circle_COMOB` | Do circle animation on COMOB. | 1581 |
| `Wave_COMOB` | Do wave animation on COMOB. | 1633 |
| `Bounce_handler` | Bounce COMOB behaviour handler. | 1706 |
| `Oscillate_handler` | Oscillate COMOB behaviour handler. | 1762 |
| `Trail_handler` | Trail COMOB behaviour handler. | 1854 |
| `Shadow_handler` | Shadow COMOB behaviour handler. | 1943 |
| `Fairy_handler` | Fairy COMOB behaviour handler. | 1993 |
| `Dust_handler` | Fairy dust COMOB behaviour handler. | 2089 |
| `Animcontrol_handler` | Animcontrol COMOB behaviour handler. | 2202 |
| `Add_trail_to_COMOB` | Add a trail of COMOBs to a COMOB. | 2285 |
| `Add_shadow_to_COMOB` | Add a shadow COMOB to a COMOB. | 2355 |
| `Add_halo_to_COMOB` | Add a halo to a COMOB. | 2428 |
| `Draw_combat_grid` | Draw combat grid. | 2543 |
| `COMOB_is_legal` | Check if a COMOB is legal. | 2633 |

### COMSHOW.C

`src/ALBION/SRC/COMBAT/COMSHOW.C` – Darstellung der Kampfaktionen: Angriffe, Treffer, Abwehr von Gruppe und Monstern.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Combat_show` | Show a certain kind of behaviour. | 290 |
| `Party_show_close_range` | Show party close-range attack behaviour. | 352 |
| `Party_show_long_range` | Show party long-range attack / projectile behaviour. | 450 |
| `Party_show_damage` | Show party receiving damage behaviour. | 483 |
| `Party_show_deflect` | Show party deflecting behaviour. | 560 |
| `Standard_monster_show_init` | Initialize standard monster show. | 592 |
| `Standard_monster_show_exit` | Exit standard monster show. | 707 |
| `Standard_monster_show_move` | Show standard monster movement behaviour. | 735 |
| `Standard_monster_show_close_range` | Show standard monster close-range attack behaviour. | 826 |
| `Standard_monster_show_long_range` | Show standard monster long-range attack / projectile behaviour. | 862 |
| `Standard_monster_show_flee` | Show standard monster fleeing behaviour. | 907 |
| `Standard_monster_show_cast_spell` | Show standard monster spell-casting behaviour. | 954 |
| `Standard_monster_show_damage` | Show standard monster receiving damage behaviour. | 984 |
| `Standard_monster_show_death` | Show standard monster dying behaviour. | 1074 |
| `Standard_monster_show_deflect` | Show standard monster deflecting behaviour. | 1198 |
| `Standard_monster_show_appear` | Show standard monster appearing behaviour. | 1230 |
| `Fear_show_init` | Initialize Fear show. | 1279 |
| `Warniak_show_init` | Initialize Warniak show. | 1345 |
| `Warniak_show_death` | Show Warniak death. | 1392 |
| `Storm_show_init` | Initialize Storm show. | 1479 |
| `Show_moving_projectile` | Show a moving projectile. | 1549 |
| `Prepare_COMOB_movement` | Prepare a COMOB for movement from a participant to a target square in the tactical grid. | 1751 |
| `Set_COMOB_vector` | Calculate the movement vector for a COMOB moving at a certain speed towards a certain target. | 1840 |
| `Determine_COMOB_flip` | Determine if a COMOB moving towards a certain target should be flipped. | 1919 |
| `Get_part_rectangle` | Get the 3D rectangle that covers a combat participant. | 1983 |
| `Get_3D_part_coordinates` | Get the 3D coordinates of a combat participant. | 2049 |
| `Convert_tactical_to_3D_coordinates` | Convert tactical to 3D coordinates. | 2138 |
| `Lock_part_damage_frame` | Lock a combat participant in the damage frame. | 2189 |
| `Unlock_part_damage_frame` | Unlock a combat participant from the damage frame. | 2244 |

### MONLOGIC.C

`src/ALBION/SRC/COMBAT/MONLOGIC.C` – Monster-KI: Taktik, Aktion wählen, Ziel wählen, Zauber wählen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Get_monster_tactic` | Get the pointer to a monster's tactic data. | 199 |
| `Select_monster_action` | Select an action for a monster. | 236 |
| `Select_offensive_monster_action` | Select an offensive monster action. | 337 |
| `Try_magical_attack` | Try making a magical attack. | 428 |
| `Count_enemies_in_row` | Count a participant's enemies in a particular row. | 661 |
| `Select_random_enemy` | Randomly select one of a participant's enemies. | 708 |
| `Choose_monster_spell` | Choose a spell for a monster. | 803 |
| `Try_long_range_attack` | Try making a long-range attack. | 882 |
| `Select_long_range_target` | Select a long-range target. | 1001 |
| `Try_close_range_attack` | Try making a close-range attack. | 1061 |
| `Select_close_range_target` | Select a close-range target. | 1176 |
| `Make_offensive_move` | Make an offensive move. | 1272 |
| `Make_offensive_horizontal_move` | Make an offensive horizontal move. | 1419 |
| `Get_targets_within_movement_range` | Get all close-range targets within a participant's movement range. | 1509 |
| `Select_defensive_monster_action` | Select a defensive monster action. | 1566 |
| `Make_defensive_horizontal_move` | Make a defensive horizontal move. | 1711 |
| `Check_move_left` | Check if move to the left is possible. | 1776 |
| `Check_move_right` | Check if move to the right is possible. | 1820 |
| `Search_and_equip_new_weapon` | Search and equip a new weapon for a combat participant. | 1867 |
| `Choose_monster_target` | Choose a target for a monster. | 2101 |
| `Check_if_long_range_weapon_has_ammo` | Check if a long-range weapon has the right ammo, if any. | 2172 |
| `Default_decider` | Default monster logic flee-or-attack decision function. | 2253 |
| `Rinrii_decider` | Special monster logic flee-or-attack decision function : only flees if one or more monsters were killed. | 2303 |
| `Kritha_decider` | Special monster logic flee-or-attack decision function : only flees if there are less monsters than party members. | 2338 |
| `Mage_decider` | Special monster logic flee-or-attack decision function : only flees if it is in close-range of the party. | 2382 |
| `Kizz_target_select` | Select the weakest target. | 2425 |
| `AI_target_select` | Do not select Tom. | 2484 |
| `Warniak_1_attack_result` | Cause condition as the result of an attack. | 2544 |
| `Warniak_2_attack_result` | Cause condition as the result of an attack. | 2577 |
| `Warniak_3_attack_result` | Cause condition as the result of an attack. | 2624 |
| `AI_attack_result` | Kill as the result of an attack. | 2677 |

### TACTICAL.C

`src/ALBION/SRC/COMBAT/TACTICAL.C` – Taktikfenster im Kampf: Felder, Teilnehmer, Aktionen per Maus eingeben.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_Tactical_window_object` | Initialize method of Tactical window object. | 265 |
| `Draw_Tactical_window_object` | Draw method of Tactical window object. | 337 |
| `Update_Tactical_window_object` | Update method of Tactical window object. | 367 |
| `Customkeys_Tactical_window_object` | Custom keys method of Tactical window object. | 397 |
| `Init_Tactical_square_object` | Initialize method of Tactical square object. | 446 |
| `Draw_Tactical_square_object` | Draw method of Tactical square object. | 481 |
| `Feedback_Tactical_square_object` | Feedback method of Tactical square object. | 513 |
| `Highlight_Tactical_square_object` | Highlight method of Tactical square object. | 550 |
| `Left_Tactical_square_object` | Left method of Tactical square object. | 587 |
| `DLeft_Tactical_square_object` | DLeft method of Tactical square object. | 635 |
| `Right_Tactical_square_object` | Right method of Tactical square object. | 681 |
| `Touch_Tactical_square_object` | Touch method of Tactical square object. | 718 |
| `Help_Tactical_square_object` | Help method of Tactical square object. | 808 |
| `Pop_up_Tactical_square_object` | Pop-up method of Tactical square object. | 939 |
| `Tactical_square_PUM_evaluator` | Evaluate tactical square pop-up menu. | 1008 |
| `PUM_No_action` | No action (tactical square pop-up menu). | 1247 |
| `PUM_Attack_tactical_square` | Attack (tactical square pop-up menu). | 1277 |
| `PUM_Move_tactical_square` | Move (tactical square pop-up menu). | 1401 |
| `PUM_Cast_spell_tactical_square` | Cast spell (tactical square pop-up menu). | 1467 |
| `PUM_Use_magic_item_tactical_square` | Use magic item (tactical square pop-up menu). | 1508 |
| `PUM_Flee_tactical_square` | Flee (tactical square pop-up menu). | 1562 |
| `PUM_Advance_tactical_square` | Advance (tactical square pop-up menu). | 1595 |
| `PUM_View_combat` | View combat (tactical square pop-up menu). | 1711 |
| `PUM_Exit_combat` | Exit combat (tactical square pop-up menu). | 1749 |
| `PUM_Combat_Main_menu` | Enter main menu (tactical square pop-up menu). | 1805 |
| `Start_combat_round` | Start combat round (button). | 1829 |
| `Draw_tactical_window` | Draw the tactical window. | 1853 |
| `Draw_tactical_squares` | Draw all tactical squares. | 1931 |
| `Draw_tactical_icons` | Draw all tactical icons. | 2028 |
| `Init_tactical_window_background` | Initialize tactical window background management. | 2159 |
| `Exit_tactical_window_background` | Exit tactical window background management. | 2200 |
| `Get_tactical_window_background` | Get tactical window background. | 2227 |
| `Restore_tactical_window_background` | Restore the tactical window's background. | 2265 |
| `Select_tactical_square` | Let the user select a tactical square. | 2305 |
| `Tactical_select_ModInit` | Initialize tactical selection module. | 2350 |
| `Tactical_select_ModExit` | Exit tactical selection module. | 2388 |
| `Show_potential_attack_targets` | Show potential attack targets in the tactical window. | 2419 |
| `Show_potential_move_targets` | Show potential movement targets in the tactical window. | 2480 |
| `Show_potential_row_targets` | Show potential row targets in the tactical window. | 2573 |
| `Show_participant_targets` | Show a participant's targets in the tactical window. | 2633 |
| `Show_participant_magic_targets` | Show a participant's magic targets. | 2720 |
| `Check_party_combat_actions` | Check the validity of the combat actions of all party members. | 2855 |
| `Check_party_member_combat_action` | Check the validity of the combat actions of a party member. | 2890 |
| `Check_party_member_magic_combat_action_targets` | Check if the target of a party member's magical combat action is still valid. | 3179 |

## Kampfmagie

### COMMAG0.C

`src/ALBION/SRC/COMMAGIC/COMMAG0.C` – Kampfzauber der Magieklasse 0: Bildeffekte und Wirkung je Zauber (Zaubernamen stehen in der Tabelle).

| Funktion | Zweck | Zeile |
|---|---|---|
| `show_samenkorn` | Combat effect: let a seed fly from the caster to a target position. **R** | 77 |
| `C0_Spell_1_handler` | Spell handler. *(Lame Monster)* | 149 |
| `Do_C0_Spell_1` | Class 0 spell 1: effect on one target. **R** | 171 |
| `C0_Spell_4_handler` | Spell handler. *(Hurry)* | 347 |
| `Do_C0_Spell_4` | Class 0 spell 4: magic effect on a party member and a temporary effect. **R** | 370 |
| `C0_Spell_5_handler` | Spell handler. *(Show LP)* | 409 |
| `C0_Spell_6_handler` | Spell handler. *(Freeze Bomb Single)* | 550 |
| `Do_C0_Spell_6` | Class 0 spell 6: ice effect on one target. **R** | 572 |
| `C0_Spell_7_handler` | Spell handler. *(Freeze Bomb row)* | 852 |
| `C0_Spell_8_handler` | Spell handler. *(Freeze Bomb all)* | 1189 |
| `C0_Spell_10_handler` | Spell handler. *(Blind single Monster)* | 1521 |
| `Do_C0_Spell_10` | Class 0 spell 10: beam effect on one target. **R** | 1543 |
| `C0_Spell_11_handler` | Spell handler. *(Blind row of Monsters)* | 1721 |
| `C0_Spell_12_handler` | Spell handler. *(Blind all Monsters)* | 1995 |
| `C0_Spell_13_handler` | Spell handler. *(Make Monster Sleep)* | 2269 |
| `Do_C0_Spell_13` | Class 0 spell 13: fairy and halo effect on one target. **R** | 2291 |
| `C0_Spell_14_handler` | Spell handler. *(Trap)* | 2588 |
| `Do_C0_Spell_14` | Class 0 spell 14: place a trap on a combat square. **R** | 2610 |
| `Handle_C0_Spell_14_trap` | Trap handler. | 2737 |
| `C0_Spell_15_handler` | Spell handler. *(Remove Trap)* | 3010 |
| `Do_C0_Spell_15` | Class 0 spell 15: stars and sparks on one target. **R** | 3032 |
| `C0_Spell_20_handler` | Spell handler. *(Fungification)* | 3172 |
| `Do_C0_Spell_20` | Class 0 spell 20: mushroom effect on one target. **R** | 3195 |

### COMMAG1.C

`src/ALBION/SRC/COMMAGIC/COMMAG1.C` – Kampfzauber der Magieklasse 1.

| Funktion | Zweck | Zeile |
|---|---|---|
| `C1_Spell_4_handler` | Spell handler. *(Blink)* | 67 |
| `C1_Spell_6_handler` | Spell handler. *(Flee)* | 523 |
| `C1_Spell_9_handler` | Spell handler. *(Mega Killer Spell)* | 618 |
| `C1_Spell_10_handler` | Spell handler. *(Irritate)* | 888 |
| `Do_C1_Spell_10` | Class 1 spell 10: effect on one target. **R** | 910 |

### COMMAG2.C

`src/ALBION/SRC/COMMAGIC/COMMAG2.C` – Kampfzauber der Magieklasse 2.

| Funktion | Zweck | Zeile |
|---|---|---|
| `C2_Spell_1_handler` | Spell handler. *(Berserker)* | 63 |
| `Do_C2_Spell_1` | Class 2 spell 1: magic effect on a party member and a temporary effect. **R** | 86 |
| `C2_Spell_2_handler` | Spell handler. *(Expel Ghost Single)* | 123 |
| `Do_C2_Spell_2` | Class 2 spell 2: beam effect on one target. **R** | 145 |
| `C2_Spell_3_handler` | Spell handler. Expel Ghost row | 344 |
| `C2_Spell_4_handler` | Spell handler. Expel Ghost all | 370 |
| `C2_Spell_5_handler` | Spell handler. *(Long range Combat Spell on a single Monster)* | 396 |
| `Do_C2_Spell_5` | Class 2 spell 5: fireball and fire ring on one target. **R** | 418 |
| `C2_Spell_6_handler` | Spell handler. *(Magical Defence)* | 636 |
| `Do_C2_Spell_6` | Class 2 spell 6: temporary effect on a party member. **R** | 658 |
| `C2_Spell_8_handler` | Spell handler. *(Scare one)* | 712 |
| `Do_C2_Spell_8` | Class 2 spell 8: scaled silhouettes that scare a monster. **R** | 734 |
| `C2_Spell_9_handler` | Spell handler. *(Scare row)* | 992 |
| `C2_Spell_10_handler` | Spell handler. *(Scare all)* | 1018 |

### COMMAG3.C

`src/ALBION/SRC/COMMAGIC/COMMAG3.C` – Kampfzauber der Magieklasse 3.

| Funktion | Zweck | Zeile |
|---|---|---|
| `C3_Spell_1_handler` | Spell handler. *(Feuerball)* | 72 |
| `Do_C3_Spell_1` | Class 3 spell 1: fireball and fire ring on one target. **R** | 94 |
| `C3_Spell_2_handler` | Spell handler. *(Blitzschlag Long-range combat spell on single Monster (energy))* | 326 |
| `Do_C3_Spell_2` | Class 3 spell 2: energy balls with trails on one target. **R** | 348 |
| `C3_Spell_3_handler` | Spell handler. *(Long-range combat spell on a row of Monsters (fire) Feuerregen)* | 773 |
| `C3_Spell_4_handler` | Spell handler. *(Long-range combat spell on a row of monsters (energy) Blitzstrahl)* | 979 |
| `C3_Spell_5_handler` | Spell handler. *(Long-range combat spell on all monsters (fire) Feuerhagel)* | 1417 |
| `C3_Spell_6_handler` | Spell handler. *(Long-range combat spell on all monsters (energie) Blitzsturm)* | 1820 |
| `C3_Spell_7_handler` | Spell handler. *(Energie Falle setzen Blitzfalle)* | 2258 |
| `Do_C3_Spell_7` | Class 3 spell 7: place a trap on a combat square. **R** | 2280 |
| `Handle_C3_Spell_7_trap` | Trap handler. Energie Falle explodiert | 2499 |
| `C3_Spell_8_handler` | Spell handler. *(Energie Falle in einer Reihe Große Blitzfalle)* | 2836 |
| `C3_Spell_9_handler` | Spell handler. Magische Falle setzten Blitzmine | 2864 |
| `Do_C3_Spell_9` | Class 3 spell 9: place a trap on a combat square. **R** | 2886 |
| `Handle_C3_Spell_9_trap` | Trap handler. *(Magische Falle explodiert)* | 3104 |
| `C3_Spell_10_handler` | Spell handler. *(Magische Falle in einer Reihe Große Blitzmine)* | 3269 |
| `C3_Spell_11_handler` | Spell handler. LP-Sucker *(Leben stehlen LP-Sucker)* | 3303 |
| `Do_C3_Spell_11` | Class 3 spell 11: halos and balls on one target. **R** | 3325 |
| `C3_Spell_12_handler` | Spell handler. *(SP-Sucker Magie stehlen)* | 3627 |
| `Do_C3_Spell_12` | Class 3 spell 12: halos and balls on one target. **R** | 3649 |
| `C3_Spell_13_handler` | Spell handler. *(Personal Defence Persöhnlicher Schutz)* | 3949 |
| `C3_Spell_14_handler` | Spell handler. *(Dissolve Monster Kamulos Blick)* | 4011 |
| `Do_C3_Spell_14` | Class 3 spell 14: charging balls, light and flash on one target. **R** | 4035 |
| `C3_Spell_15_handler` | Spell handler. *(Remove Traps Falle entfernen)* | 4392 |
| `Do_C3_Spell_15` | Class 3 spell 15: stars and sparks on one target. **R** | 4414 |

### COMMAG4.C

`src/ALBION/SRC/COMMAGIC/COMMAG4.C` – Kampfzauber der Magieklasse 4 (Panik, Vergiftung, Reizung, Krankheit verursachen).

| Funktion | Zweck | Zeile |
|---|---|---|
| `C4_Spell_1_handler` | Spell handler (Cause panic). | 63 |
| `Do_C4_Spell_1` | Class 4 spell 1: cloud flying to one target. **R** | 85 |
| `C4_Spell_2_handler` | Spell handler (Cause poisoning). | 160 |
| `Do_C4_Spell_2` | Class 4 spell 2: cloud flying to one target. **R** | 182 |
| `C4_Spell_3_handler` | Spell handler (Cause irritation). | 257 |
| `Do_C4_Spell_3` | Class 4 spell 3: cloud flying to one target. **R** | 279 |
| `C4_Spell_4_handler` | Spell handler (Cause disease). | 354 |
| `Do_C4_Spell_4` | Class 4 spell 4: cloud flying to one target. **R** | 376 |

### COMMSUB.C

`src/ALBION/SRC/COMMAGIC/COMMSUB.C` – Hilfsfunktionen für Zaubereffekte: Funken, Schweife, Halos, Flammen, Schnee, Verhaltensbehandler für COMOBs.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Do_build_spell_target_list` | Add a combat participant to the list of spell targets (called for every target by Do_all_magic_combat_targets). **R** | 71 |
| `Gen_COMOB` | Create a COMOB at a 3D position with the given lifespan, size, graphics and draw mode. **R** | 124 |
| `ip3d` | Wert interpolieren | 203 |
| `aip3d` | Wert mit zunehmender Beschleunigung interpolieren | 234 |
| `dip3d` | Wert mit abnehmender Beschleunigung interpolieren | 277 |
| `calc_strength` | Scale the spell strength (1...100) linearly into the range min...max (also works if max < min). **R** | 329 |
| `calc_delta_xyz` | Calculate the movement vector from a start to a target position for steps of a given length. **R** | 382 |
| `rndmm` | Return a random number between min and max (inclusive). **R** | 465 |
| `rndmm2` | Return a random number from one of two ranges, each chosen with a chance of 50 %. **R** | 507 |
| `update_n_times` | Update the combat screen at least once and then until the given time has passed. **R** | 553 |
| `Add_halo_to_COMOB_2` | Add a halo to a COMOB. | 604 |
| `Gen_Funken` | Create a number of animated sparks at a 3D position. **R** | 734 |
| `Gen_Sparks` | Create a number of sparks that fly from a 3D position in random directions and bounce on the floor. **R** | 852 |
| `groundglow` | Show a glow on the ground at a position for a while. **R** | 963 |
| `makeflame` | Create an animated flame at a 3D position. **R** | 1067 |
| `gen_Dummy_COMOB` | Create an invisible helper COMOB (used as anchor for behaviours). **R** | 1167 |
| `Dissolve` | Dissolve a monster into a grid of small coloured COMOBs taken from its graphics. **R** | 1253 |
| `Test_COMOB_mask` | Check if a 3D position lies on a visible (non-transparent) pixel of a COMOB. **R** | 1450 |
| `Get_COMOB_max_size` | Get maximum size of COMOB source Animation frames graphics. | 1511 |
| `Show_flashstar` | Show a star at a 3D position that grows and shrinks again. **R** | 1573 |
| `Add_schweif` | Add a trail of COMOBs behind a COMOB. **R** | 1639 |
| `Show_deflect` | Show a ring effect when a spell is deflected by a participant. **R** | 1736 |
| `size_handler` | Behaviour handler: shrink a COMOB step by step and delete it at the minimum size. **R** | 1871 |
| `size_II_handler` | Behaviour handler: let a COMOB grow to a maximum width, shrink again and delete it at the minimum. **R** | 1962 |
| `size_III_handler` | Behaviour handler: let a COMOB grow and shrink between a minimum and a maximum width. **R** | 2066 |
| `flash_handler` | Behaviour handler: flash the palette for a moment. **R** | 2162 |
| `glow_handler` | Behaviour handler: recolour the palette step by step (glow). **R** | 2263 |
| `snow_handler` | Behaviour handler: move a snowflake with random acceleration and delete it at the limits. **R** | 2318 |
| `snow_II_handler` | Behaviour handler: keep creating new snowflakes (at a position, at random or in a row). **R** | 2417 |
| `FireBounce_handler` | Behaviour handler: fireball with gravity and air friction that creates sparks when it hits the floor. **R** | 2563 |
| `Oscillate_II_handler` | Oscillate COMOB behaviour handler. | 2720 |
| `CrazyMove_handler` | Behaviour handler: move a COMOB with changing random acceleration. **R** | 2834 |
| `connect_handler` | Behaviour handler: keep a COMOB at the position and size of another COMOB. **R** | 2953 |
| `funken_handler` | Behaviour handler: follow another COMOB and emit sparks. **R** | 3019 |
| `groundglow_handler` | Behaviour handler: keep a ground glow below another COMOB. **R** | 3090 |
| `lifedead_handler` | Behaviour handler: when the lifespan of a COMOB runs out, replace it with a new COMOB. **R** | 3158 |
| `Fairy_II_handler` | Behaviour handler of a fairy that leaves dust. **R** | 3271 |
| `Dust_II_handler` | Fairy dust COMOB behaviour handler. | 3386 |
| `Animcontrol_II_handler` | Animcontrol COMOB behaviour handler. Im Gegensatz zum normalen animcontrol_handler wird das COMOB am Ende nicht gelöscht sondern verbleibt in der letzten Phase | 3515 |
| `Trail_II_handler` | Trail COMOB behaviour handler. only X and Y | 3595 |
| `Gravity_handler` | Behaviour handler: apply gravity to a COMOB and delete it below a given height. **R** | 3658 |
| `Party_magic_effect` | Show the magic effect on a party member. **R** | 3702 |
| `Add_schweif` | Add a trail of COMOBs behind a COMOB (variable distance). **R** *(aus)* | 3857 |
| `Offset_handler` | shapes=3; *(aus)* | 3944 |
| `Trail_II_handler` | Trail COMOB behaviour handler. only X and Y *(aus)* | 3992 |

## Karten

### 2D_COLL.C

`src/ALBION/SRC/MAP/2D_COLL.C` – 2D-Karte: Bewegung und Kollision, Gleiten an Hindernissen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Make_2D_move` | Make a move in a 2D map. | 78 |
| `Try_2D_move` | Check if a certain move can be made in a 2D map. | 177 |
| `Try_big_guy_2D_move` | Check if a big guy can make a certain move in a 2D map. | 327 |
| `Try_small_guy_2D_move` | Check if a small guy can make a certain move in a 2D map. | 813 |
| `Try_double_slide_2D` | Try to slide first in one, then in the opposite direction in a 2D map. | 1074 |
| `Try_to_slide_2D` | Try to slide in a direction in a 2D map. | 1124 |
| `Slide_2D` | Slide in a direction in a 2D map. | 1167 |
| `Special_2D_high_check` | Check if an icon in a 2D map can be passed behind diagonally. | 1213 |
| `Special_2D_low_check` | Check if an icon in a 2D map can be passed over diagonally. | 1297 |
| `Double_movement_check_2D` | Check if a certain position in a 2D map can be moved to. | 1429 |
| `Extra_vertical_movement_check_2D` | Check if a vertical movement in a large-scale 2D map is possible. | 1495 |
| `Do_check_2D` | Check if a certain position in a 2D map can be moved to. | 1537 |
| `Check_2D_NPC_collision` | Check if a certain position in the 2D map is blocked by an NPC. | 1659 |
| `Sucking_chairs_2D` | Handle sucking chairs in 2D maps. | 1728 |

### 2D_DISPL.C

`src/ALBION/SRC/MAP/2D_DISPL.C` – 2D-Karte: Zeichnen von Untergrund, Überlagerungen und Objekten im Scrollpuffer.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Prepare_2D_display` | Prepare internal variables for display. | 137 |
| `Calculate_2D_camera_target_position` | Calculate the desired position of the camera in a 2D map. | 195 |
| `Draw_2D_map` | Draw all objects and animated parts of the 2D map. | 229 |
| `Redraw_2D_objects` | Redraw all 2D objects. | 482 |
| `Draw_2D_scroll_buffer` | Draw the 2D map scroll buffer. | 559 |
| `Display_extra_icons` | Display extra icons covering any objects. | 596 |
| `Display_underlay` | Display an underlay in the scroll buffer. | 695 |
| `Display_overlay` | Display an overlay in the scroll buffer. | 766 |
| `Display_2D_object` | Display a 2D object in the scroll buffer. | 834 |
| `Swap_2D_objects` | Swap two 2D objects (for sorting). | 878 |
| `Compare_2D_objects` | Compare two 2D objects (for sorting). | 908 |
| `Set_animation_update` | Mark animated map squares that must be updated. | 956 |
| `Update_2D_map_area` | Update a 2D map area. | 1018 |
| `Update_2D_screen_area` | Update a 2D screen area. | 1059 |
| `Set_update_rectangle` | Set update rectangle. | 1112 |
| `Redraw_2D_map` | Redraw the entire 2D map. | 1215 |
| `Set_erase_rectangles` | Set update rectangles from previous frame. | 1250 |
| `Fill_map_buffer` | Fill map buffer. | 1338 |
| `Clear_2D_object_list` | Clear the 2D object list. | 1446 |
| `Add_2D_object` | Add a 2D object to the list. | 1471 |
| `Set_2D_camera_position` | Set the position of the 2D map camera. | 1504 |
| `Get_2D_camera_position` | Get the position of the 2D map camera. | 1531 |
| `Set_2D_camera_target_position` | Set the target position of the 2D map camera. | 1558 |
| `Get_2D_camera_target_position` | Get the target position of the 2D map camera. | 1585 |
| `Move_2D_camera` | Move the position of the 2D map camera. | 1612 |
| `Lock_2D_camera` | Lock the 2D map camera. | 1638 |
| `Unlock_2D_camera` | Unlock the 2D map camera. | 1667 |
| `Update_2D_unit` | Updates a scroll unit of the 2D map. | 1698 |
| `Display_underlay_diagnostics` | Draw blocked travel modes/directions of an underlay icon (diagnostic mode). **R** | 1805 |
| `Display_overlay_diagnostics` | Draw blocked travel modes/directions of an overlay icon (diagnostic mode). **R** | 1866 |
| `Display_event_diagnostics` | Mark map squares that have event triggers (diagnostic mode). **R** | 1957 |

### 2D_MAP.C

`src/ALBION/SRC/MAP/2D_MAP.C` – 2D-Karte (Draufsicht): Modul, Hauptschleife, Mausbewegung.

| Funktion | Zweck | Zeile |
|---|---|---|
| `M2_ModInit` | Initialize 2D map module. | 213 |
| `M2_ModExit` | Exit 2D map module. | 329 |
| `M2_DisInit` | Initialize 2D map display. | 363 |
| `M2_DisExit` | Exit 2D map display. | 416 |
| `M2_MainLoop` | 2D map main loop. | 460 |
| `Display_2D_map` | Display the 2D map. | 509 |
| `Touched_2D_object` | Touched method of 2D map object. | 584 |
| `Left_2D_object` | Left method of 2D map object. | 620 |
| `Right_2D_object` | Right method of 2D map object. | 660 |
| `Customkeys_2D_object` | Custom keys method of 2D map object. | 691 |
| `Move_mouse_M2_ModInit` | Initialize 2D map mouse move mode module. | 749 |
| `Move_mouse_M2_ModExit` | Exit 2D map mouse move mode module. | 787 |
| `Move_mouse_M2_MainLoop` | 2D map movement main loop. | 815 |
| `Mouse_move_2D` | Move in 2D mouse move mode. | 864 |
| `Move_key_M2_ModInit` | Initialize 2D map key move mode module. | 952 |
| `Move_key_M2_ModExit` | Exit 2D map key move mode module. | 980 |
| `Move_key_M2_MainLoop` | 2D map key movement main loop. | 1005 |
| `Key_move_2D` | Move in 2D key move mode. | 1055 |
| `Select_M2_MainLoop` | 2D map selection mode main loop. | 1129 |
| `Display_M2_selection` | Display 2D map selection. | 1168 |
| `Select_M2_ModInit` | Initialize 2D map selection mode module. | 1206 |
| `Select_M2_ModExit` | Exit 2D map selection mode module. | 1304 |
| `Get_2D_mouse_state` | Get state of mouse in 2D map window. | 1336 |
| `Search_2D_party_member` | Search for a party member in the current map. | 1407 |
| `Convert_2D_map_to_screen_coordinates` | Convert 2D map to screen coordinates. | 1486 |
| `Map_to_2D` | Convert map to 2D coordinates. | 1526 |
| `_2D_to_map` | Convert 2D to map coordinates. | 1567 |
| `Initialize_2D_position` | Set the position in the 2D map. | 1611 |
| `Init_2D_light_state` | Initialise 2D light state. | 1647 |
| `Get_target_2D_light_state` | Calculate target light state in a target map. | 1675 |
| `Update_2D_light_state` | Update the light state in a 2D map. | 1739 |
| `Set_2D_light_state` | Blend the map palette depending on the 2D light state. | 1784 |

### 2D_PATH.C

`src/ALBION/SRC/MAP/2D_PATH.C` – 2D-Karte: Pfad und Spur der Gruppe (die Mitglieder laufen hintereinander).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_2D_party_path` | Initialize the 2D map party and path. | 109 |
| `Exit_2D_party_path` | Exit the 2D map party and path. | 172 |
| `Init_2D_party_member` | Initialize a 2D map party member. | 202 |
| `Exit_2D_party_member` | Exit a 2D map party member. | 272 |
| `Reset_2D_path` | Reset the 2D map path. | 302 |
| `Init_2D_trail_data` | Init the 2D map trail data. | 373 |
| `Add_member_to_2D_trail` | Add a party member to the 2D map trail. | 432 |
| `Remove_member_from_2D_trail` | Remove a party member from the 2D map trail. | 485 |
| `Change_active_member_2D_path` | Change the active member in the 2D map path. | 538 |
| `Update_2D_party_position` | Update the positions of the party objects in the 2D map. | 694 |
| `Store_2D_movement` | Store a map-square movement in the 2D path. | 840 |
| `Store_2D_current_position` | Store a the current position in the 2D path. | 884 |
| `Make_2D_path_entry` | Make a single entry in the 2D path. | 914 |
| `Display_2D_party` | Display party members in a 2D map. | 958 |

### 3D_MAP.C

`src/ALBION/SRC/MAP/3D_MAP.C` – 3D-Karte (Ego-Sicht): Modul, Hauptschleife, Rendern.

| Funktion | Zweck | Zeile |
|---|---|---|
| `M3_ModInit` | Initialize 3D map module. | 184 |
| `M3_ModExit` | Exit 3D map module. | 263 |
| `M3_DisInit` | Initialize 3D map display. | 296 |
| `M3_DisExit` | Exit 3D map display. | 372 |
| `M3_MainLoop` | 3D map main loop. | 411 |
| `Display_3D_map` | Display the 3D map. | 450 |
| `Render_3D_map` | Render the 3D map. | 602 |
| `Init_3DM_library` | Initialize 3DM library. | 701 |
| `Touched_3D_object` | Touched method of 3D map object. | 850 |
| `Left_3D_object` | Left method of 3D map object. | 901 |
| `Right_3D_object` | Right method of 3D map object. | 1026 |
| `Customkeys_3D_object` | Custom keys method of 3D map object. | 1059 |
| `Error_3DM` | Report a 3DM error. | 1143 |
| `Set_3D_window_size` | Set 3D window size. | 1188 |
| `Init_shade_factor` | Initialise shade factor. | 1251 |
| `Get_target_shade_factor` | Calculate target shade factor. | 1286 |
| `Update_shade_factor` | Update shade factor. | 1378 |

### 3D_MOVE.C

`src/ALBION/SRC/MAP/3D_MOVE.C` – 3D-Karte: Position, Drehen, Bewegen, Maussteuerung.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Initialize_3D_position` | Set the position in the 3D dungeon. | 152 |
| `Get_3D_mouse_state` | Get state of mouse in 3D map window. | 192 |
| `Get_3D_mouse_state2` | Get state of mouse in 3D map window, including the corners. | 268 |
| `Rotate_3D` | Change the camera angle in the 3D dungeon. | 376 |
| `Add_3D_vector` | Move along a vector in the 3D dungeon. | 402 |
| `Move_mouse_M3_ModInit` | Initialize 3D map mouse move mode module. | 469 |
| `Move_mouse_M3_ModExit` | Exit 3D map mouse move mode module. | 508 |
| `Move_mouse_M3_MainLoop` | 3D map mouse movement main loop. | 536 |
| `Mouse_move_3D` | Move in 3D mouse move mode. | 585 |
| `Move_key_M3_ModInit` | Initialize 3D map key move mode module. | 790 |
| `Move_key_M3_ModExit` | Exit 3D map key move mode module. | 818 |
| `Move_key_M3_MainLoop` | 3D map key movement main loop. | 843 |
| `Key_move_3D` | Move in 3D key move mode. | 893 |
| `Make_3D_party_move` | The party makes a move in a 3D map. | 1053 |
| `Make_3D_move` | Make a move in a 3D map. | 1134 |
| `Try_3D_move` | Check if a certain move can be made in a 3D map. | 1267 |
| `Get_3D_edge_area` | Classify a position inside a 3D map square as centre or edge area. **R** | 1555 |
| `Movement_check_3D` | Check if a certain position in a 3D map can be moved to. | 1605 |
| `Check_3D_object_group_collision` | Check if a certain position in a 3D map causes collision with an object group. | 1728 |
| `Map_to_3D` | Convert map to 3D coordinates. | 1799 |
| `_3D_to_map` | Convert 3D to map coordinates. | 1834 |
| `Check_if_line_in_3D_map_is_blocked` | Check if a line between two positions in a 3D map is blocked. | 1874 |

### 3D_PREP.C

`src/ALBION/SRC/MAP/3D_PREP.C` – 3D-Karte: Böden, Decken, Wände und Objekte laden und umrechnen, Schattierungstabellen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_3D_data` | Initialize 3D data. | 200 |
| `Exit_3D_data` | Exit 3D data. | 342 |
| `Make_all_shade_tables` | Make all shade tables. | 401 |
| `Load_3D_floors` | Load and convert floors and ceilings. | 466 |
| `Allocate_floor_buffer` | Allocate a floor buffer. | 593 |
| `Load_3D_textures` | Load and convert object and wall textures. | 643 |
| `Copy_texture` | Copy and convert a texture. | 958 |
| `Copy_texture2` | Copy a texture into the 3D texture buffer, converting it on the way. **R** | 1000 |
| `Position_3D_textures` | Determine the position of 3D textures. | 1051 |
| `Swap_3D_textures` | Swap two 3D textures (for sorting). | 1171 |
| `Compare_3D_textures` | Compare two 3D textures (for sorting). | 1210 |
| `Compare_3D_textures2` | Compare two 3D textures (for sorting). | 1249 |
| `Load_3D_overlays` | Load and convert overlays. | 1283 |
| `Init_shade_tables_for_transparent_walls` | Initialise shade tables for transparent walls. | 1350 |
| `Exit_shade_tables_for_transparent_walls` | Exit shade tables for transparent walls. | 1415 |
| `Calculate_shade_tables_for_transparent_walls` | Calculate shade tables for transparent walls. | 1455 |
| `Put_unanimated_overlays_on_unanimated_walls` | Put un-animated overlays on un-animated walls. | 1529 |
| `Put_overlays_on_walls` | Put possibly animated overlays on possibly animated walls. | 1628 |
| `Get_object_graphics` | Return pointer to object graphics. | 1741 |
| `Get_floor_graphics` | Return pointer to floor graphics. | 1847 |
| `Get_wall_graphics` | Return pointer to wall graphics. | 1890 |
| `Get_wall_shade_table` | Return pointer to wall shade table. | 1940 |
| `Put_overlay_on_wall` | Put an overlay on a wall. | 1970 |
| `Remove_overlay_from_wall` | Remove an overlay from a wall. | 2035 |
| `Colour_cycle_forward_3D` | Cycle colours forward in the 3D shading table. | 2076 |
| `Calculate_shade_table` | Calculate a shade table for the 3D map. | 2141 |
| `Relocate_on_256_byte_boundary` | Relocate a memory block on a 256 byte boundary. | 2212 |
| `Texture_vanish_test` | Test if a texture may vanish when shaded away. *(aus)* | 2249 |
| `Convert_lab_data` | Convert 3D LAByrinth data (file converter function). | 2297 |
| `Calculate_shade_function` | Calculate a shade function for the 3D map. | 2379 |
| `Get_shade_table_address` | Get the address of the 3D shade table. | 2447 |

### 3D_SEL.C

`src/ALBION/SRC/MAP/3D_SEL.C` – 3D-Karte: Auswahlmodus (auf etwas in der 3D-Sicht zeigen).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Select_M3_ModInit` | Initialize 3D map select mode module. | 95 |
| `Select_M3_ModExit` | Exit 3D map select mode module. | 154 |
| `Select_M3_MainLoop` | 3D map selection mode main loop. | 182 |
| `Interpret_3D_identification_data` | Interpret 3D identification data. | 321 |
| `Get_distance_to_selected_map_square` | Calculate_distance between party and selected map square. | 486 |
| `Check_line_to_selected_map_square` | Check the line between party and selected map square. | 525 |

### ICCHANGE.C

`src/ALBION/SRC/MAP/ICCHANGE.C` – Kartenänderungen (geöffnete Türen, entfernte Objekte …), die dauerhaft gespeichert werden.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_modifications` | Initialize modification list. | 101 |
| `Exit_modifications` | Exit modification list. | 199 |
| `Destroy_modification_list` | Free a chain of map modification lists. **R** | 216 |
| `Prepare_modifications_for_saving` | Prepare a modification list for saving. | 256 |
| `Make_modifications` | Make modifications to a map. | 339 |
| `Clone_modifications` | Clone modifications of one map to another map. | 408 |
| `Add_permanent_modification` | Add a new modification to the permanent list. | 479 |
| `Check_for_double_permanent_modification` | Check if a modification already exists in the permanent list, and remove it if this is the case. | 576 |
| `Add_temporary_modification` | Add a new modification to the temporary list. | 656 |
| `Check_for_double_temporary_modification` | Check if a modification already exists in the temporary list, and remove it if this is the case. | 753 |
| `Remove_modification` | Remove a modification from a modification list. | 832 |
| `Do_change_icon` | Change an icon. | 968 |
| `Replace_2D_cutmap_block` | Replace a 2D map part with a cut-map block. | 1267 |
| `Mix_2D_cutmap_block` | Mix a 2D map part with a cut-map block. | 1382 |

### MAP.C

`src/ALBION/SRC/MAP/MAP.C` – Kartenrahmen: Karte betreten und verlassen, Palette, Anzeige, gemeinsame Kartenlogik.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_map` | Initialize a new map | 174 |
| `Exit_map` | Leave the current map. | 477 |
| `Init_map_display` | Initialize map display. | 550 |
| `Exit_map_display` | Exit map display. | 581 |
| `Update_map_display` | Update map display. | 609 |
| `Update_map_stuff` | Update map stuff. | 638 |
| `Init_map_palette` | Initialise map palette. | 697 |
| `Reset_map_palette_blending` | Reset the map palette blending. | 836 |
| `Update_map_palette` | Update the map palette. | 872 |
| `Blend_map_palette` | Blend the map palette. | 953 |
| `Get_target_map_blending_percentage` | Get the target map blending percentage. | 1061 |
| `Colour_cycle_forward_2D` | Cycle colours forward in a 2D map. | 1093 |
| `Get_map_data_offsets` | Calculate offsets into map data. | 1129 |
| `Set_music` | Set normal and ambient music. | 1232 |
| `Before_move` | Before move logic. | 1284 |
| `After_move` | After move logic. | 1334 |
| `Time_after_move` | After move time logic. | 1359 |
| `Game_after_move` | After move game logic. | 1382 |
| `Execute_normal_map_events` | Execute normal map events. | 1407 |
| `Get_location_status` | Get the status of a location. | 1484 |
| `Seek_transport` | Seek a transportation. | 1729 |
| `Create_transport` | Create a transportation. | 1777 |
| `Find_Goto_point_data_in_map` | Find goto-point data in a map file. | 1822 |
| `Vision_blocked` | Check if a certain position in a 3D map blocks vision. | 1893 |
| `Get_combat_background_nr` | Get combat background number. | 1982 |
| `Change_position` | Change the position of the party in the current map. | 2032 |
| `Save_position` | Save current player position. | 2071 |
| `Restore_position` | Restore position. | 2117 |

### MAP_PUM.C

`src/ALBION/SRC/MAP/MAP_PUM.C` – Aufklappmenü auf der Karte (Reden, Untersuchen, Benutzen, Nehmen, Transportmittel).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Map_PUM_evaluator` | Evaluate map pop-up menu. | 114 |
| `PUM_Map_Talk` | Talk (map pop-up menu). | 511 |
| `PUM_Map_Examine` | Examine (map pop-up menu). | 669 |
| `PUM_Map_Manipulate` | Manipulate (map pop-up menu). | 725 |
| `PUM_Map_Use_item` | Use item (map pop-up menu). | 781 |
| `PUM_Map_Take_item` | Take item (map pop-up menu). | 876 |
| `PUM_Map_Change_transport` | Change transport (map pop-up menu). | 932 |
| `PUM_Map_Enter_automapper` | Enter the automapper (map pop-up menu). | 956 |
| `PUM_Map_Build_camp` | Build a camp (map pop-up menu). | 980 |
| `PUM_Map_Wait` | Wait (map pop-up menu). | 1012 |
| `PUM_Map_Main_menu` | Enter main menu (map pop-up menu). | 1055 |

### SPECITEM.C

`src/ALBION/SRC/MAP/SPECITEM.C` – Besondere Gegenstände mit Anzeige auf der Karte: Kompass, Uhr, Monsteraugen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_special_items` | Initialize special items. | 131 |
| `Init_compass` | Initialize compass special item. | 182 |
| `Init_clock` | Initialize clock special item. | 248 |
| `Exit_special_items` | Exit special items. | 314 |
| `Exit_compass` | Exit compass special item. | 357 |
| `Exit_clock` | Exit clock special item. | 383 |
| `Show_special_items` | Show special items. | 409 |
| `Hide_special_items` | Hide special items. | 433 |
| `Display_special_items_2D` | Diplay special items in a 2D map. | 489 |
| `Prepare_2D_special_items_display` | Set up the display of the special items for the 2D map. **R** | 555 |
| `Display_special_items_3D` | Diplay special items in a 3D map. | 605 |
| `Update_compass` | Update compass special item. | 732 |
| `Update_clock` | Update clock special item. | 787 |

## Textsystem

### TEXT.C

`src/ALBION/SRC/TEXT/TEXT.C` – Textsystem: Textstil-Stapel, Druckbereiche, Fehlermeldungen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Text_error` | Report a text processor error. | 46 |
| `Text_print_error` | Print a text processor error. | 74 |
| `Reset_textstyle_stack` | Reset the text style stack. | 113 |
| `Push_textstyle` | Pushes a new text style on the text style stack. | 141 |
| `Pop_textstyle` | Pops a text style from the top of the textstyle stack. | 176 |
| `Change_textstyle` | Change the text style on the top of the text style stack. | 208 |
| `Reset_PA_stack` | Reset the PA stack. | 233 |
| `Push_PA` | Pushes a new PA on the PA stack. | 262 |
| `Pop_PA` | Pops a PA from the top of the PA stack. | 305 |
| `Change_PA` | Change the PA on the top of the PA stack. | 349 |
| `Init_PA` | Initialize a PA. | 377 |

### TEXTCOMM.C

`src/ALBION/SRC/TEXT/TEXTCOMM.C` – Text-Steuerbefehle innerhalb von Texten (Stil, Schrift, Farbe, Ausrichtung).

| Funktion | Zweck | Zeile |
|---|---|---|
| `LLC_handler` | Low level text command handler. | 59 |
| `Get_LLC_nr` | Get 3-digit number from text command. | 165 |
| `LLC_Set_ink` | Low level text commands. | 192 |
| `LLC_Set_shadow` | Text command: set the shadow colour. **R** | 209 |
| `LLC_No_shadow` | Text command: switch the shadow off. **R** | 226 |
| `LLC_Set_normal_style` | Text command: normal text style. **R** | 243 |
| `LLC_Set_fat_style` | Text command: fat text style. **R** | 260 |
| `LLC_Set_high_style` | Text command: high text style. **R** | 277 |
| `LLC_Set_fat_high_style` | Text command: fat and high text style. **R** | 294 |
| `LLC_Set_big_style` | Text command: big text style. **R** | 311 |
| `LLC_Set_normal_font` | Text command: normal font. **R** | 328 |
| `LLC_Set_techno_font` | Text command: techno font. **R** | 345 |
| `LLC_Set_capital` | Text command: start a coloured capital letter. **R** | 362 |
| `LLC_Unset_capital` | Text command: end the capital letter. **R** | 382 |
| `LLC_Default` | Text command: back to the default text style. **R** | 400 |
| `LLC_HJump` | Text command: move the cursor to the right. **R** | 421 |
| `LLC_VJump` | Text command: increase the line spacing. **R** | 443 |
| `LLC_Set_centered` | Text command: centred text. **R** | 465 |
| `LLC_Set_left` | Text command: left-aligned text. **R** | 482 |
| `LLC_Set_right` | Text command: right-aligned text. **R** | 499 |
| `LLC_Set_justified` | Text command: justified text. **R** | 516 |

### TEXTDISP.C

`src/ALBION/SRC/TEXT/TEXTDISP.C` – Text ausgeben: links, rechts, zentriert, im Kasten, printf-artig.

| Funktion | Zweck | Zeile |
|---|---|---|
| `xprintf` | Print a normal string, using a printf-like format. | 66 |
| `Print_string` | Print a normal string. | 111 |
| `Print_right_string` | Print a normal string, right-justified. | 271 |
| `Print_centered_string` | Print a normal string, centered horizontally. | 314 |
| `Print_centered_line_string` | Print a normal string, centered horizontally, on a line. | 357 |
| `Print_centered_box_string` | Print a normal string, centered horizontally AND vertically. | 414 |
| `Print_processed_string` | Print a processed: string. | 462 |
| `Print_normal_string` | Print a normal string. | 559 |
| `Print_justified_string` | Print a justified string. | 712 |
| `Prepare_justification` | Prepare a text line for justification. | 878 |
| `Print_character` | Print a normal character. | 958 |
| `Print_fat_character` | Print a fat character. | 1010 |
| `Print_high_character` | Print a high character. | 1062 |
| `Print_fat_high_character` | Print a fat high character. | 1114 |
| `Print_big_character` | Print a big character. | 1166 |
| `Get_line_width` | Get the width in pixels of a text line. | 1212 |
| `Get_line_size` | Get the width and height in pixels of a text line. | 1358 |

### TEXTGFX.C

`src/ALBION/SRC/TEXT/TEXTGFX.C` – Einzelne Zeichen in ein OPM zeichnen (normal, fett, hoch, groß).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Put_character` | Put a character in an OPM. | 46 |
| `Put_fat_character` | Put a fat character in an OPM. | 167 |
| `Put_high_character` | Put a high character in an OPM. | 296 |
| `Put_fat_high_character` | Put a fat, high character in an OPM. | 425 |
| `Put_big_character` | Put a big character in an OPM. | 562 |

### TEXTMNG.C

`src/ALBION/SRC/TEXT/TEXTMNG.C` – Texte aufbereiten und anzeigen, Textfenster, Druckbereiche.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Get_text_size` | Get the height and number of lines in a processed text. | 84 |
| `Process_and_display_text` | Process and display a single text. | 122 |
| `Destroy_processed_text` | Destroy a processed text. | 165 |
| `Display_processed_text` | Display a processed text. | 215 |
| `Refresh_text_window` | Refresh the current text window. | 498 |
| `Erase_print_area` | Erase the print area. | 687 |
| `Init_print_area` | Prepare a print area for printing. | 763 |
| `Exit_print_area` | Exit a print area. | 857 |
| `Cache_text_line` | Cache a line of text. | 901 |
| `Destroy_cached_text_line` | Destroy a cached text line. | 980 |
| `Destroy_text_cache` | Destroy all cached text lines. | 1016 |
| `Find_cached_text_line` | Find a text line among the cached text lines. | 1050 |
| `Print_cached_string` | Print a cached text line. | 1091 |
| `Find_free_text_line_cache` | Find a free entry among the cached text lines. | 1120 |
| `Update_text_cache_priorities` | Update the priorities of the text cache entries. | 1172 |

### TEXTPROC.C

`src/ALBION/SRC/TEXT/TEXTPROC.C` – Textumbruch: Rohtext in Zeilen zerlegen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Process_text` | Process a single text. | 68 |
| `Process_text_list` | Process a list of texts. | 102 |
| `Find_wrap_position` | Find the position where a line should be wrapped. | 549 |
| `Write_processed_line` | Write a line of processed text from the text processing buffer. | 710 |
| `Analyze_line` | Analyze a text line. | 897 |
| `Read_raw_line` | Read a line of raw text into the text processing buffer. | 1142 |

### TEXTVAR.C

`src/ALBION/SRC/TEXT/TEXTVAR.C` – Variablen des Textsystems.

Keine Funktionen (nur Daten).

## Oberfläche

### BOOLREQ.C

`src/ALBION/SRC/UI/BOOLREQ.C` – Ja/Nein-Abfragen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Boolean_requester` | Display and handle a boolean requester window. | 107 |
| `Boolean_requester_with_buttons` | Display and handle a boolean requester window. | 139 |
| `Init_BooleanReq_object` | Initialize method of Boolean requester window object. | 193 |
| `Draw_BooleanReq_object` | Draw method of Boolean requester window object. | 274 |
| `BooleanReq_Yes` | Yes (button). | 340 |
| `BooleanReq_No` | No (button). | 374 |

### BUTTONS.C

`src/ALBION/SRC/UI/BUTTONS.C` – Schaltflächen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_Button_object` | Initialize method of Button object. | 97 |
| `Draw_Button_object` | Draw method of Button object. | 135 |
| `Feedback_Button_object` | Feedback method of Button object. | 314 |
| `Highlight_Button_object` | Highlight method of Button object. | 487 |
| `Left_Button_object` | Left method of Button object. | 831 |
| `Help_Button_object` | Help method of Button object. | 984 |
| `Set_Button_object` | Set method of Button object. | 1029 |
| `Get_Button_object` | Get method of Button object. | 1068 |
| `Draw_Radio_group_object` | Draw method of Radio_group object. | 1097 |
| `Set_Radio_group_object` | Set method of Radio_group object. | 1126 |
| `Get_Radio_group_object` | Get method of Radio_group object. | 1176 |
| `Find_radio_button` | Find a radio button with a certain number in a radio group. | 1206 |

### COLOURS.C

`src/ALBION/SRC/UI/COLOURS.C` – Paletten: laden, überblenden, Farbzyklen, Umfärben.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Reset_palette_fading` | Reset palette fading. | 72 |
| `Init_palette` | Initialize the palette. | 103 |
| `Load_palette` | Load a palette. | 170 |
| `Update_palette` | Update the palette. | 237 |
| `Activate_palette` | Fade the current palette and activate it. | 295 |
| `Protect_colours` | Protect the cycled colours in the current palette. | 361 |
| `Cycle_colours` | Cycled colours in a palette. | 420 |
| `Calculate_recolouring_table` | Calculate a recolouring table for the current palette. | 507 |
| `Recolour_palette` | Recolour the current palette. | 555 |
| `Blend_palette` | Blend and set the current palette. | 596 |
| `Colour_cycle_forward` | Cycle colours forward in a palette. | 663 |
| `Fade_to_black` | Fade the bottom 192 colours to black. | 758 |
| `Fade_to_white` | Fade the bottom 192 colours to white. | 794 |
| `Fade_from_black` | Fade the bottom 192 colours from black. | 830 |
| `Fade_from_white` | Fade the bottom 192 colours from white. | 865 |

### CONTROL.C

`src/ALBION/SRC/UI/CONTROL.C` – Eingabe und Objektsystem der Oberfläche: Ereignisse, Maus, Ziehen und Ablegen, Methodenaufrufe, Objektbaum.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Enter_drag_drop_mode` | Enter drag & drop mode. | 243 |
| `Leave_drag_drop_mode` | Leave drag & drop mode. | 278 |
| `Abort_drag_drop_mode` | Abort drag & drop mode. | 306 |
| `Get_event` | Get an input event and handle input recording / playback. | 332 |
| `Wait_4_user` | Wait for the user to click or press a key. | 447 |
| `Check_if_user_acted` | Check if the user has clicked or pressed a key. | 495 |
| `Wait_4_click` | Wait for the user to click the left mouse button. | 540 |
| `Wait_4_unclick` | Wait for the user to release the left mouse button. | 574 |
| `Wait_4_right_unclick` | Wait for the user to release the right mouse button. | 603 |
| `Update_input` | Update input. | 635 |
| `Handle_input` | Handle input. | 667 |
| `Clear_input_buffer` | Clear the input buffer. | 772 |
| `Handle_mouse_event` | Handle mouse event. | 806 |
| `Search_mouse_event_object` | Search an object which can handle the current mouse event. | 999 |
| `Search_mouse_method` | Search a certain method or the custommouse method in an object. | 1079 |
| `Predict_method_capability` | Look for an object which can handle the current mouse method. | 1156 |
| `Handle_key_event` | Handle key event. | 1234 |
| `Add_object` | Create an instance of an object class and bind it into the current object tree. | 1380 |
| `Search_object` | Search an object in the object tree, starting at a given object. | 1502 |
| `Delete_object` | Remove an object from the current tree and destroy it. | 1570 |
| `Add_object_to_pool` | Add an object to the object pool. | 1692 |
| `Remove_object_from_pool` | Remove an object from the object pool. | 1769 |
| `Execute_method` | Execute an object's method. | 1836 |
| `Execute_child_methods` | Execute an object's childrens' method. | 1893 |
| `Execute_broadcast_method` | Execute a method for every object. | 1953 |
| `Do_execute_broadcast_method` | Call a method on an object and all objects below it. **R** | 2017 |
| `Execute_upcast_method` | Execute a method for one of an object's parents which can handle the method. | 2072 |
| `Change_object_size` | Change an object's size. | 2132 |
| `Change_object_position` | Change an object's position. | 2169 |
| `Do_get_object_data` | Get an object's data. | 2204 |
| `Is_object_present` | Check if an object is present. | 2258 |
| `Wait_4_object` | Wait until an object is deleted. | 2304 |
| `Has_method` | Check if an object has a certain method. | 2369 |
| `Is_over_object` | Check if the mouse is over an object. | 2420 |
| `Delete_self` | Delete self. | 2469 |
| `Object_at` | Find an object at a certain position. | 2498 |
| `Find_object_at` | Find the topmost object at a screen position. **R** | 2519 |
| `Disable_object` | Disable an object. | 2604 |
| `Enable_object` | Enable an object. | 2636 |
| `Push_root` | Push a new root on the root stack. | 2668 |
| `Pop_root` | Pops a root from the top of the root stack. | 2708 |
| `Reset_root_stack` | Reset the root stack. | 2754 |
| `Set_root_OPM` | Set the OPM of the current root. | 2806 |
| `Get_root_object_handle` | Get the handle of the current root object. | 2840 |
| `Clear_object_pool` | Clear the object pool. | 2864 |
| `Push_module` | Push a new module on the module stack. | 2927 |
| `Pop_module` | Pops a module from the top of the module stack. | 3005 |
| `Reset_module_stack` | Reset the module stack. | 3053 |
| `Init_module` | Initialize a new module. | 3103 |
| `Exit_module` | Terminate a module. | 3132 |
| `Main_loop` | Call current module's MainLoop function. | 3165 |
| `Init_display` | Call current module's DisInit function. | 3196 |
| `Exit_display` | Call current module's DisExit function. | 3227 |
| `Update_display` | Call current module's DisUpd function. | 3258 |
| `Current_screen_type` | Get current module's screen type. | 3308 |
| `Set_screen_type` | Set the current module's screen type. | 3354 |
| `Init_mouse_system` | Initialise the mouse pointer system. | 3379 |
| `Exit_mouse_system` | Exit the mouse pointer. | 3428 |
| `Push_mouse` | Push a new mouse pointer on the mouse pointer stack. | 3467 |
| `Pop_mouse` | Pops a mouse pointer from the top of the mouse pointer stack. | 3500 |
| `Change_mouse` | Change the mouse pointer on the top of the mouse pointer stack. | 3532 |
| `Init_mouse_pointer` | Initialize a new mouse pointer. | 3562 |
| `Write_chunk_name` | Write a four-character chunk name. | 3642 |
| `Mouse_on` | Show the mouse pointer. | 3673 |
| `Mouse_off` | Hide the mouse pointer. | 3710 |
| `Push_MA` | Push a new mouse area on the MA stack. | 3743 |
| `Pop_MA` | Pops a mouse area from the top of the MA stack. | 3776 |
| `Reset_MA_stack` | Reset the mouse area stack. | 3808 |
| `Change_MA` | Change the mouse area on top of the MA stack. | 3842 |
| `Init_MA` | Initialize a new mouse area. | 3868 |
| `Update_screen` | Update the screen. | 3900 |
| `Switch_screens` | Display the currently invisible screen. | 3926 |
| `Add_update_OPM` | Add an OPM to the update list. | 4014 |
| `Remove_update_OPM` | Remove an OPM from the update list. | 4064 |
| `Show_OPMs` | Show all OPMs in the update list. | 4104 |
| `Show_changed_OPMs` | Show all changed OPMs in the update list. | 4235 |
| `Report_control_error` | Report a control error. | 4294 |

### FONT.C

`src/ALBION/SRC/UI/FONT.C` – Schriften: Breitentabellen, Unterschneidung (Kerning), Zeichensatz-Übersetzung, Tintenfarbe und Stil.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_font` | Load and prepare fonts. | 309 |
| `Exit_font` | Terminate fonts. | 364 |
| `Prepare_font` | Initialize a font. | 389 |
| `Set_ink` | Set the current printing ink colour. | 452 |
| `Set_style` | Set the current printing ink style. | 479 |

### INPUT.C

`src/ALBION/SRC/UI/INPUT.C` – Texteingabe in einem Fenster.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Input_string_in_window` | Input a string in a window. | 154 |
| `Input_string` | Input a string. | 278 |
| `Input_ModInit` | Init input module. | 322 |
| `Input_ModExit` | Exit input module. | 353 |
| `Init_Input_object` | Init method of Input object. | 385 |
| `Exit_Input_object` | Exit method of Input object. | 441 |
| `Update_Input_object` | Update method of Input object. | 476 |
| `Customkeys_Input_object` | Custom keys method of Input object. | 539 |
| `Left_Input_object` | Left mouse button method of Input object. | 661 |
| `Right_Input_object` | Right mouse button method of Input object. | 692 |

### INPUTNR.C

`src/ALBION/SRC/UI/INPUTNR.C` – Zahleneingabe in einem Fenster (auch mit Nachkommastelle).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Input_number` | Display and handle a number input window. | 187 |
| `Input_number_with_symbol` | Display and handle a number input window with a symbol. | 257 |
| `Input_broken_number` | Display and handle a number input window for a broken number. | 325 |
| `Input_broken_number_with_symbol` | Display and handle a number input window with a symbol for a broken number. | 396 |
| `Init_InputNr_object` | Initialize method of Number input window object. | 462 |
| `Print_broken_number` | Format a value in tenths as "x.y". **R** | 549 |
| `Draw_InputNr_object` | Draw method of Number input window object. | 574 |
| `InputNr_Exit` | Accept value (button). | 668 |
| `Init_Number_bar_object` | Initialize method of Number bar object. | 693 |
| `Draw_Number_bar_object` | Draw method of Number bar object. | 782 |
| `Get_Number_bar_object` | Get method of Number bar object. | 820 |
| `Set_Number_bar_object` | Set method of Number bar object. | 849 |
| `Left_Number_bar_object` | Left method of Number bar object. | 904 |
| `Number_bar_page_up` | Move the slider up one page. | 1047 |
| `Number_bar_page_down` | Move the slider down one page. | 1108 |
| `Light_number_slider` | Light a number bar's slider. | 1169 |
| `Update_number_slider` | Update a number bar's slider. | 1206 |
| `Do_draw_number_bar` | Draw a number bar. | 1246 |
| `Number_bar_1_up` | Increase value by one (button). | 1439 |
| `Number_bar_1_down` | Decrease value by one (button). | 1515 |

### ITEMLIST.C

`src/ALBION/SRC/UI/ITEMLIST.C` – Gegenstandslisten mit Plätzen und Rollbalken.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_Item_list_object` | Initialize method of Item list object. | 117 |
| `Draw_Item_list_object` | Draw method of Item list object. | 230 |
| `Restore_Item_list_object` | Restore method of Item list object. | 289 |
| `Update_item_list` | Update the item list (scroll bar function). | 345 |
| `Init_Item_slot_object` | Initialize method of Item slot object. | 389 |
| `Draw_Item_slot_object` | Draw method of Item slot object. | 423 |
| `Update_Item_slot_object` | Update method of Item slot object. | 472 |
| `Feedback_Item_slot_object` | Feedback method of Item slot object. | 554 |
| `Highlight_Item_slot_object` | Highlight method of Item slot object. | 599 |
| `Pop_up_Item_slot_object` | Pop-up method of Item slot object. | 645 |
| `Help_Item_slot_object` | Help method of Item slot object. | 717 |
| `Right_Item_slot_object` | Right method of Item slot object. | 833 |
| `Touch_Item_slot_object` | Touch method of Item slot object. | 873 |
| `Extract_slot_packet` | Make a COPY of an item packet belonging to an item slot object. | 918 |
| `Claim_slot_packet` | Claim the pointer to an item packet belonging to an item slot object. | 967 |
| `Free_slot_packet` | Free the pointer to an item packet belonging to an item slot object. | 1011 |
| `Find_item_slot_object` | Find an item slot object belonging to an item list. | 1044 |
| `Draw_item_slot_item` | Draw the item of an item slot object. | 1103 |
| `Draw_item` | Draw an item. | 1146 |
| `Draw_body_item` | Draw a body item. | 1218 |

### ITEMSEL.C

`src/ALBION/SRC/UI/ITEMSEL.C` – Fenster „Gegenstand auswählen“.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Select_party_member_item` | Select an item from a party member's inventory. | 159 |
| `Init_ItemSel_object` | Initialize method of Item selection window object. | 322 |
| `Draw_ItemSel_object` | Draw method of Item selection window object. | 383 |
| `Draw_SelItem_object` | Draw method of Item slot object. | 447 |
| `Feedback_SelItem_object` | Feedback method of Item slot object. | 515 |
| `Highlight_SelItem_object` | Highlight method of Item slot object. | 580 |
| `Left_SelItem_object` | Left method of Selectable item slot object. | 646 |

### MEMBRSEL.C

`src/ALBION/SRC/UI/MEMBRSEL.C` – Fenster „Gruppenmitglied auswählen“.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Select_party_member` | Select a party member. | 168 |
| `Init_MemberSel_object` | Initialize method of Member selection window object. | 287 |
| `Draw_MemberSel_object` | Draw method of Member selection window object. | 364 |
| `Abort_MemberSel_object` | Abort method of Member selection window object. | 431 |
| `Init_SelMember_object` | Init method of Selectable member object. | 473 |
| `Draw_SelMember_object` | Draw method of Selectable member object. | 507 |
| `Feedback_SelMember_object` | Feedback method of Selectable member object. | 590 |
| `Highlight_SelMember_object` | Highlight method of Selectable member object. | 662 |
| `Help_SelMember_object` | Help method of Selectable member object. | 736 |
| `Left_SelMember_object` | Left method of Selectable member object. | 778 |

### POPUP.C

`src/ALBION/SRC/UI/POPUP.C` – Aufklappmenüs (PUM).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Do_PUM` | Display and handle a pop-up menu. | 160 |
| `Do_centered_PUM` | Display and handle a pop-up menu centered in an area. | 318 |
| `Init_PUM_object` | Initialize method of PUM object. | 478 |
| `Draw_PUM_object` | Draw method of PUM object. | 547 |
| `Init_PUME_object` | Initialize method of PUME object. | 609 |
| `Draw_PUME_object` | Draw method of PUME object. | 643 |
| `Feedback_PUME_object` | Feedback method of PUME object. | 692 |
| `Highlight_PUME_object` | Highlight method of PUME object. | 741 |
| `Left_PUME_object` | Left method of PUME object. | 790 |

### SCROLBAR.C

`src/ALBION/SRC/UI/SCROLBAR.C` – Rollbalken.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_Scroll_bar_object` | Initialize method of Scrollbar object. | 113 |
| `Draw_Scroll_bar_object` | Draw method of Scrollbar object. | 190 |
| `Set_Scroll_bar_object` | Set method of Scrollbar object. | 229 |
| `Get_Scroll_bar_object` | Get method of Scrollbar object. | 278 |
| `Left_Scroll_bar_object` | Left method of Scrollbar object. | 307 |
| `Scroll_bar_page_up` | Move the slider up one page. | 446 |
| `Scroll_bar_page_down` | Move the slider down one page. | 490 |
| `Light_slider` | Light the slider. | 533 |
| `Update_slider` | Update the slider. | 570 |
| `Do_draw_scroll_bar` | Draw a scroll bar. | 611 |

### SELWIN.C

`src/ALBION/SRC/UI/SELWIN.C` – Allgemeines Auswahlfenster mit Liste.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Do_select_window` | Let the user select something. | 183 |
| `Init_Select_window_object` | Init method of Select window object. | 289 |
| `Draw_Select_window_object` | Draw method of Select window object. | 469 |
| `Update_Selectable_list` | Update the Selectable list (scroll bar function). | 540 |
| `Init_Selectable_object` | Init method of Selectable object. | 584 |
| `Draw_Selectable_object` | Draw method of Selectable object. | 618 |
| `Feedback_Selectable_object` | Feedback method of Selectable object. | 692 |
| `Highlight_Selectable_object` | Highlight method of Selectable object. | 774 |
| `Left_Selectable_object` | Left method of Selectable object. | 857 |

### TEXTWIN.C

`src/ALBION/SRC/UI/TEXTWIN.C` – Textfenster (Meldungen, Bücher, Schilder).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Do_text_file_window` | Draw and handle a text window containing a text block from a text file. | 62 |
| `Do_text_file_window_with_symbol` | Draw and handle a text window containing a text block from a text file, with a symbol. | 103 |
| `Do_text_window` | Draw and handle a text window. | 147 |
| `Do_text_window_with_symbol` | Draw and handle a text window with a symbol. | 348 |

### USERFACE.C

`src/ALBION/SRC/UI/USERFACE.C` – Fenster und Grundelemente der Oberfläche: Fenster öffnen und schließen, Rahmen, Kästen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Restore_object_background` | Restore the background of an object. | 116 |
| `Draw_children` | Draw method of Earth object. | 152 |
| `Restore_slab` | Slab restore method. | 180 |
| `Window_ModInit` | Initialize window module. | 220 |
| `Window_ModExit` | Exit window module. | 287 |
| `Exit_Window_object` | Exit method of Window object. | 351 |
| `Close_Window_object` | Close method of Window object. | 385 |
| `Draw_Window_object` | Draw method of Window object. | 416 |
| `Restore_window` | Restore method of Window object. | 481 |
| `Prepare_window` | Prepare a window. | 529 |
| `Destroy_window` | Destroy a window. | 621 |
| `Draw_window_inside` | Draw the inside of a window. | 671 |
| `Draw_window_border` | Draw a window border. | 755 |
| `Draw_high_border` | Draw a high border. | 872 |
| `Draw_deep_border` | Draw a deep box. | 938 |
| `Draw_deep_box` | Draw a deep box. | 1004 |
| `Draw_light_box` | Draw a light box. | 1049 |
| `Normal_touched` | Normal touch interaction. | 1122 |
| `Dehighlight` | Remove current highlighting. | 1237 |
| `Normal_clicked` | Normal left-click interaction. | 1287 |
| `Normal_rightclicked` | Normal right-click interaction. | 1369 |
| `Wipe_out` | Wipe a screen area out (showing the slab). | 1443 |
| `Load_small_picture` | Load a small picture. | 1482 |
| `Destroy_small_picture` | Destroy the currently loaded small picture. | 1564 |
| `Display_small_picture_centered` | Display the currently loaded small picture centered in an area. | 1601 |
| `Display_LBM` | Display an LBM picture. | 1644 |
| `Get_LBM_dimensions` | Get the dimensions of an LBM picture. | 1683 |
| `Find_LBM_chunk` | Find a chunk in an LBM file. | 1741 |
| `Set_LBM_palette` | Set the palette from an LBM file. | 1796 |
| `Display_LBM_image` | Display the image from an LBM file. | 1855 |

## Hilfsmodule

### FASTFLC.C

`src/ALBION/SRC/EXTRA/FASTFLC.C` – Schnelles Abspielen von FLIC-Videos.

| Funktion | Zweck | Zeile |
|---|---|---|
| `FASTFLC_Start_flic_playback` | Start playing back a flic. | 82 |
| `FASTFLC_Restart_flic` | Go back to frame 0 of the current flic. | 189 |
| `FASTFLC_Stop_flic_playback` | Stop playing back the current flic. | 219 |
| `FASTFLC_Playback_flic_frame` | Play back a frame in the current flic. | 256 |
| `FASTFLC_Decode_frame_chunk` | Decode a frame chunk from the current flic. | 437 |
| `FASTFLC_Decode_COLOR_256_chunk` | Decode a COLOR_256 FLC-chunk. | 552 |
| `FASTFLC_Decode_DELTA_FLC_chunk` | Decode a DELTA_FLC FLC-chunk. | 631 |
| `FASTFLC_Decode_COLOR_64_chunk` | Decode a COLOR_64 FLC-chunk. | 777 |
| `FASTFLC_Decode_DELTA_FLI_chunk` | Decode a DELTA_FLI FLC-chunk. | 856 |
| `FASTFLC_Decode_BLACK_chunk` | Decode a BLACK FLC-chunk. | 968 |
| `FASTFLC_Decode_BYTE_RUN_chunk` | Decode a BYTE_RUN FLC-chunk. | 1001 |
| `FASTFLC_Decode_LITERAL_chunk` | Decode a LITERAL FLC-chunk. | 1082 |

### FINDCOL.C

`src/ALBION/SRC/EXTRA/FINDCOL.C` – Nächstliegende Farbe in einer Palette finden, geschützte Farben.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Prepare_colour_find` | Prepare a palette for colour-finding. | 87 |
| `Find_closest_colour` | Search a palette for the colour which best matches a certain target colour. | 147 |
| `Swap_colours` | Swap two colours (for sorting). | 337 |
| `Compare_colours` | Compare two colours (for sorting). | 370 |
| `Clear_protected_colours` | Remove all colours from the protected colour list. | 399 |
| `Add_protected_colours` | Add colours to protected colour list. | 430 |
| `Remove_protected_colours` | Remove colours from protected colour list. | 461 |
| `Find_closest_colour` | Search a palette for the colour which best matches a certain target colour. *(aus)* | 495 |

### FLC.C

`src/ALBION/SRC/EXTRA/FLC.C` – Aufnehmen von FLIC-Videos (Entwicklerwerkzeug).

| Funktion | Zweck | Zeile |
|---|---|---|
| `FLC_Start_flic_recording` | Start recording a flic. | 111 |
| `FLC_Stop_flic_recording` | Stop recording the current flic. | 243 |
| `FLC_Record_flic_frame` | Record a frame in the current flic. | 344 |
| `FLC_Create_COLOR_256_chunk` | Create a COLOR_256 FLC-chunk. | 431 |
| `FLC_Create_BYTE_RUN_chunk` | Create a BYTE_RUN run-length encoded FLC-chunk. | 494 |
| `FLC_Write_run_packet` | Write a byte-run RLE-packet. | 645 |
| `FLC_Write_unpacked_packet` | Write an unpacked RLE-packet. | 690 |
| `FLC_Create_DELTA_FLC_chunk` | Create a DELTA_FLC word-oriented delta-packed FLC-chunk. | 745 |
| `FLC_Scan_line_for_delta_packets` | Scan a line for delta packets. | 865 |
| `FLC_Write_delta_packet` | Run-length encode a delta packet and write it in a buffer. | 971 |
| `FLC_Write_run_delta_packet` | Write a word-run delta packet. | 1119 |
| `FLC_Write_unpacked_delta_packet` | Write an unpacked delta packet. | 1184 |
| `FLC_Start_flic_playback` | Start playing back a flic. | 1272 |
| `FLC_Restart_flic` | Go back to frame 0 of the current flic. | 1379 |
| `FLC_Stop_flic_playback` | Stop playing back the current flic. | 1409 |
| `FLC_Playback_flic_frame` | Play back a frame in the current flic. | 1446 |
| `FLC_Decode_frame_chunk` | Decode a frame chunk from the current flic. | 1627 |
| `FLC_Decode_COLOR_256_chunk` | Decode a COLOR_256 FLC-chunk. | 1742 |
| `FLC_Decode_DELTA_FLC_chunk` | Decode a DELTA_FLC FLC-chunk. | 1821 |
| `FLC_Decode_COLOR_64_chunk` | Decode a COLOR_64 FLC-chunk. | 2010 |
| `FLC_Decode_DELTA_FLI_chunk` | Decode a DELTA_FLI FLC-chunk. | 2089 |
| `FLC_Decode_BLACK_chunk` | Decode a BLACK FLC-chunk. | 2215 |
| `FLC_Decode_BYTE_RUN_chunk` | Decode a BYTE_RUN FLC-chunk. | 2252 |
| `FLC_Decode_LITERAL_chunk` | Decode a LITERAL FLC-chunk. | 2347 |
| `FLC_Error` | Report an FLC error. | 2397 |
| `FLC_Print_error` | Print an FLC error. | 2430 |

### FLCVAR.C

`src/ALBION/SRC/EXTRA/FLCVAR.C` – Variablen für FLIC.

Keine Funktionen (nur Daten).

### GFXFUNC.C

`src/ALBION/SRC/EXTRA/GFXFUNC.C` – Grafikgrundfunktionen: Blöcke kopieren, maskieren, umfärben, scrollen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Get_block` | Copies a block from an OPM to memory. | 49 |
| `Put_unmasked_block` | Put an unmasked block in an OPM. | 149 |
| `Put_masked_block` | Put a masked block in an OPM. | 265 |
| `Put_silhouette` | Put a silhouette of a block in an OPM. | 388 |
| `Put_recoloured_block` | Recolour the silhouette of a block in an OPM. | 508 |
| `Put_recoloured_box` | Recolour a box in an OPM. | 629 |
| `Scroll_block` | Scroll a block in an OPM. | 743 |
| `Put_unmasked_X_mirrored_block` | Put an unmasked block in an OPM, mirrored around the Y-axis. | 875 |
| `Put_masked_X_mirrored_block` | Put a masked block in an OPM, mirrored around the Y-axis. | 990 |
| `Put_recoloured_X_mirrored_block` | Recolour the silhouette of a block in an OPM, mirrored around the Y-axis. | 1113 |
| `Get_nr_frames` | Get the number of frames out of a standard graphics header. | 1231 |
| `Get_gfx_size` | Get size of a block out of a standard graphics header. | 1266 |
| `Draw_enlarged_block` | Draw a block in a specially enlarged way. | 1305 |

### HDOB.C

`src/ALBION/SRC/EXTRA/HDOB.C` – HDOBs: Grafikobjekte, die über dem Bild schweben (z. B. Mauszeiger-Begleiter), samt Hintergrundsicherung.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Reset_HDOBs` | Delete all current HDOBs and switch visibility on. | 80 |
| `Show_HDOBs` | Show HDOBs. | 126 |
| `Hide_HDOBs` | Hide HDOBs. | 152 |
| `Add_HDOB` | Add a HDOB to the current list. | 178 |
| `Change_HDOB` | Change a HDOB in the current list. | 238 |
| `Delete_HDOB` | Delete a HDOB from the current list. | 301 |
| `Set_HDOB_position` | Set the position of a HDOB. | 339 |
| `Draw_HDOBs` | Display HDOBs on the screen. | 368 |
| `Erase_HDOBs` | Remove HDOBs from the screen. | 535 |
| `Update_HDOBs` | Update all HDOBs. | 596 |
| `HDOB_is_ready` | Check if a HDOB is ready. | 635 |
| `Drop_HDOB` | Drop a HDOB. | 674 |
| `Init_HDOB_drop` | Initialize HDOB dropping. | 711 |
| `Drop_HDOB_handler` | HDOB handler which drops a HDOB. | 770 |
| `Vibrate_HDOB` | Vibrate a HDOB. | 835 |
| `Move_HDOB` | Move a HDOB towards a target. | 909 |
| `Move_HDOB_handler` | HDOB handler which moves a HDOB to a target. | 963 |

### SCROLL.C

`src/ALBION/SRC/EXTRA/SCROLL.C` – Scrollpuffer für die 2D-Karte.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_scroll` | Initialize scroll data. | 55 |
| `Exit_scroll` | Terminate scroll data. | 143 |
| `Set_scroll_position` | Set the position of the viewport. | 185 |
| `Fill_scroll_buffer` | Fill the scroll buffer. | 216 |
| `Do_scroll` | Scroll a viewport within a playfield. | 287 |
| `Update_scroll_rectangle` | Update a rectangle in the scroll buffer. | 470 |
| `Scroll_display` | Display the scroll viewport. | 556 |
| `Do_scroll_display` | Display a part of the scroll viewport. | 602 |
| `Scroll_display_OPM` | Display the scroll viewport in an OPM. | 672 |
| `Do_scroll_display_OPM` | Display a part of the scroll viewport in an OPM. | 709 |
| `Convert_scroll_coordinates` | Convert playfield coordinates to scroll OPM coordinates. | 774 |
| `Display_object_in_scroll_buffer` | Display an object in a scroll buffer. | 842 |

### SORT.C

`src/ALBION/SRC/EXTRA/SORT.C` – Allgemeine Sortierverfahren (Shuttlesort, Shellsort).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Shuttlesort` | Generic shuttlesort | 38 |
| `Shellsort` | Generic shellsort | 89 |

### XLOAD.C

`src/ALBION/SRC/EXTRA/XLOAD.C` – XLD-Bibliotheken: Dateien und Unterdateien laden und speichern.

| Funktion | Zweck | Zeile |
|---|---|---|
| `XLD_Load_file` | Load a file. | 166 |
| `XLD_Save_file` | Save a file. | 285 |
| `XLD_Load_standard_file` | Load a file, using just the filename. | 364 |
| `XLD_Load_XLD_library` | Load an entire XLD-library. | 396 |
| `XLD_Save_XLD_library` | Save an entire XLD-library. | 512 |
| `XLD_Get_subfile_length` | Get the length of a subfile from a library. | 545 |
| `XLD_Open_subfile` | Open a subfile from a library. | 628 |
| `XLD_Close_subfile` | Close a subfile from a library. | 736 |
| `XLD_Load_subfile` | Load a subfile from a library. | 762 |
| `XLD_Save_subfile` | Save a subfile into a library. | 877 |
| `XLD_Load_unique_subfile` | Load a unique subfile from a library. | 1035 |
| `XLD_Load_full_batch` | Load a batch of subfiles from a library. ALL files in the batch must be loaded. | 1156 |
| `XLD_Load_partial_batch` | Load a batch of subfiles from a library. NOT all files in the batch must be loaded. | 1190 |
| `XLD_Do_load_batch` | Load a batch of subfiles from a library. | 1227 |
| `XLD_Swap` | Swap two subfiles and indices (for sorting). | 1634 |
| `XLD_Compare` | Compare two subfiles (for sorting). | 1670 |
| `XLD_Do_load_subfile` | Select and execute a subfile loader. | 1702 |
| `XLD_Load_unpacked_subfile` | Load an unpacked subfile. | 1765 |
| `XLD_Open_library` | Open an XLD library. | 1866 |
| `XLD_Close_library` | Close the currently opened XLD library. | 1973 |
| `File_exists` | Check if a file exists. | 2003 |
| `Directory_exists` | Check if a directory exists. | 2053 |
| `Change_directory` | Change the current directory. | 2093 |
| `XLD_Error` | Report an XLOAD error. | 2138 |
| `XLD_Print_error` | Print an XLOAD error. | 2173 |

### ZOOMFUNC.C

`src/ALBION/SRC/ZOOMFUNC/ZOOMFUNC.C` – Gezoomte Grafik für den Kampf (Monster und Effekte in verschiedenen Größen).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Put_zoomed_block` | Put a zoomed block in an OPM. | 59 |
| `Put_zoomed_silhouette` | Put a single-colour silhouette of a zoomed block in an OPM. | 126 |
| `Put_zoomed_recoloured_silhouette` | Put a recoloured silhouette of a zoomed block in an OPM. | 195 |
| `Put_zoomed_recoloured_block` | Put a zoomed and recoloured block in an OPM. | 265 |
| `Put_zoomed_transparent_block` | Put a zoomed transparent block in an OPM. | 323 |

## Spiel

### ANIMATE.C

`src/ALBION/SRC/ANIMATE.C` – Tabellen für zyklische und zufällige Animationen (Kartenobjekte, Symbole).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_animation` | Initialize animation tables. | 41 |
| `Reset_random_animation` | Reset random animation data. | 141 |
| `Update_animation` | Update animation arrays. | 174 |
| `Get_animation_frame` | Get current animation frame. | 276 |

### APRES.C

`src/ALBION/SRC/APRES.C` – Bildschirm nach dem Kampf: Beute verteilen, Gegenstände an Gruppenmitglieder geben.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Enter_Apres_combat` | Enter Apres combat screen. | 232 |
| `Distribute_char_items` | Distribute character items screen. | 275 |
| `Apres_ModInit` | Initialize Apres combat module. | 396 |
| `Apres_ModExit` | Exit Apres combat module. | 453 |
| `Apres_DisInit` | Initialize Apres combat display. | 481 |
| `Apres_DisExit` | Exit Apres combat display. | 513 |
| `Apres_MainLoop` | Main loop of Apres combat module. | 542 |
| `Exit_Apres` | Leave the Apres combat screen. | 589 |
| `Distribute_char_items_ModInit` | Initialize Distribute character items module. | 675 |
| `Divide_EP` | Divide experience points over party members. | 730 |
| `Clear_combat_conditions` | Clear all combat-only body conditions for all party members. | 796 |
| `Init_Apres_object` | Initialize method of Apres combat object. | 836 |
| `Draw_Apres_object` | Draw method of Apres combat object. | 951 |
| `Restore_Apres_object` | Restore method of Apres combat object. | 1013 |
| `Draw_Apres_item_slot_object` | Draw method of Apres item slot object. | 1084 |
| `Feedback_Apres_item_slot_object` | Feedback method of Apres item slot object. | 1155 |
| `Highlight_Apres_item_slot_object` | Highlight method of Apres item slot object. | 1225 |
| `Left_Apres_item_slot_object` | Left method of Apres item slot object. | 1296 |
| `DLeft_Apres_item_slot_object` | DLeft method of Apres item slot object. | 1384 |
| `Drop_Apres_item_slot_object` | Drop method of Apres item slot object. | 1443 |
| `Drag_Apres_item` | Drag Apres items. | 1476 |
| `Drop_on_Apres_item` | Drop on Apres item. | 1540 |
| `Apres_item_drag_abort_handler` | Apres item drag & drop abort handler. | 1722 |
| `Apres_item_PUM_evaluator` | Evaluate Apres item pop-up menu. | 1775 |
| `PUM_Drop_Apres_item` | Drop an Apres item (Apres item pop-up menu). | 1825 |
| `PUM_Examine_Apres_item` | Examine an Apres item (Apres item pop-up menu). | 1886 |
| `Drop_Apres_items` | Drop Apres pool items. | 1926 |
| `Take_item_from_Apres_pool` | Take an item out of the Apres pool. | 1994 |
| `Put_item_in_Apres_pool` | Put an item in the Apres pool. | 2057 |
| `Auto_move_packet_to_Apres_pool` | Automatically move an item packet to the Apres pool. | 2134 |
| `Move_drag_HDOB_towards_Apres_slot` | Move drag HDOB towards a slot of the Apres combat screen. | 2274 |
| `Init_Apres_pool` | Init Apres combat pool. | 2305 |
| `Exit_Apres_pool` | Exit Apres combat pool. | 2355 |
| `Store_item_in_Apres_pool` | Store item in Apres combat pool. | 2394 |
| `Put_gold_in_Apres_pool` | Put a number of gold coins in the Apres combat pool. | 2433 |
| `Put_food_in_Apres_pool` | Put a number of food rations in the Apres combat pool. | 2458 |
| `Pool_Apres_pool` | Try to optimise the Apres combat pool. | 2483 |

### AUTOMAP.C

`src/ALBION/SRC/AUTOMAP.C` – Automap: Anzeige der erkundeten Karte, Legende, Markierungen, Scrollen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Enter_Automap` | Enter the Automap. | 281 |
| `Do_enter_automap` | Event action: open the automap. **R** | 314 |
| `Automap_ModInit` | Initialize Automap module. | 357 |
| `Automap_ModExit` | Exit Automap module. | 510 |
| `Init_Automap_display` | Initialize Automap display. | 543 |
| `Exit_Automap_display` | Exit Automap display. | 577 |
| `Display_automap` | Display the automap. | 614 |
| `Customkeys_Automap_object` | Custom keys method of Automap object. | 820 |
| `Touched_Automap_object` | Touched method of Automap object. | 870 |
| `Left_Automap_object` | Left method of Automap object. | 1033 |
| `Right_Automap_object` | Right method of Automap object. | 1112 |
| `Get_Automap_mouse_state` | Get state of mouse in Automap window. | 1142 |
| `Move_automap` | Move the automap. | 1190 |
| `Find_goto_point` | Find goto-point at a certain location. | 1248 |
| `Check_for_new_goto_points` | Check if the player has "discovered" any new goto-points. | 1298 |
| `Update_automap_unit` | Updates a scroll unit of the automap. | 1359 |
| `Init_automap` | Initialize automap. | 1407 |
| `Exit_automap` | Exit automap. | 1448 |
| `Save_automap` | Save automap. | 1476 |
| `Update_automap` | Update the Automap. | 1508 |
| `Get_automap_bit` | Get a bit from the automap. | 1984 |
| `Set_automap_bit` | Set a bit in the automap. | 2033 |
| `Create_automap_parchment_layer` | Create automap parchment layer. | 2077 |
| `Prepare_automap_floors` | Prepare the automap floors. | 2317 |
| `Shrink_floor` | Shrink a 3D floor for the automap. | 2435 |
| `Insert_automap_walls_and_floors` | Insert walls and floors in automap. | 2502 |
| `Insert_automap_events` | Insert events in automap. | 2608 |
| `Insert_automap_NPCs` | Insert NPCs in automap. | 2737 |
| `Insert_automap_goto_points` | Insert goto-points in automap. | 2893 |
| `Insert_automap_wall` | Insert a wall in the automap buffer. | 2941 |
| `Insert_automap_icon` | Insert an icon in the automap buffer. | 3036 |

### BATFORM.C

`src/ALBION/SRC/BATFORM.C` – Fenster „Kampfaufstellung“: Gruppenmitglieder auf die Startfelder im Kampf verteilen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Go_Battle_formation` | Let the user change the battle formation (button). | 179 |
| `Init_BatForm_object` | Initialize method of Battle formation window object. | 222 |
| `Exit_BatForm_object` | Exit method of Battle formation window object. | 322 |
| `Draw_BatForm_object` | Draw method of Battle formation window object. | 370 |
| `BatForm_Exit` | Exit Battle formation window (button). | 400 |
| `Init_BatFormSlot_object` | Init method of Battle formation slot object. | 425 |
| `Draw_BatFormSlot_object` | Draw method of Battle formation slot object. | 459 |
| `Feedback_BatFormSlot_object` | Feedback method of Battle formation slot object. | 534 |
| `Highlight_BatFormSlot_object` | Highlight method of Battle formation slot object. | 611 |
| `Help_BatFormSlot_object` | Help method of Battle formation slot object. | 697 |
| `Left_BatFormSlot_object` | Left method of Battle formation slot object. | 781 |
| `Drop_BatFormSlot_object` | Drop method of Battle formation slot object. | 828 |
| `Inquire_drop_BatFormSlot_object` | Inquire drop method of Battle formation slot object. | 861 |
| `Drag_BatFormSlot` | Drag Battle formation slot. | 905 |
| `Drop_on_BatFormSlot` | Drop on Battle formation slot. | 1003 |
| `BatFormSlot_drag_abort_handler` | Battle formation slot drag & drop abort handler. | 1087 |

### CAMP.C

`src/ALBION/SRC/CAMP.C` – Lager: Rasten, Heilen, Zeit vergehen lassen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Enter_Camp` | Enter Camp screen. | 100 |
| `Do_enter_camp` | Event action: open the camp screen. **R** | 128 |
| `Camp_ModInit` | Initialize Camp module. | 157 |
| `Recuperate` | Let a party member recuperate while camping. | 299 |

### CHEST.C

`src/ALBION/SRC/CHEST.C` – Truhen und verschlossene Behälter: Schloss knacken, Schlüssel, Fallen, Inhalt nehmen und ablegen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Do_Chest` | Enter Chest screen. | 269 |
| `Closed_chest_ModInit` | Initialize Closed chest module. | 351 |
| `Closed_chest_ModExit` | Exit Closed chest module. | 410 |
| `Closed_chest_DisInit` | Initialize Closed chest display. | 437 |
| `Closed_chest_DisExit` | Exit Closed chest display. | 485 |
| `Closed_chest_MainLoop` | Main loop of Closed chest module. | 515 |
| `Exit_Chest` | Leave the Chest screen. | 570 |
| `Init_Closed_chest_object` | Initialize method of Closed chest object. | 596 |
| `Draw_Closed_chest_object` | Draw method of Closed chest object. | 632 |
| `Restore_Closed_chest_object` | Restore method of Closed chest object. | 683 |
| `Open_chest_ModInit` | Initialize Open chest module. | 742 |
| `Open_chest_ModExit` | Exit Open chest module. | 866 |
| `Open_chest_DisInit` | Initialize Open chest display. | 909 |
| `Open_chest_DisExit` | Exit Open chest display. | 957 |
| `Open_chest_MainLoop` | Main loop of Open chest module. | 987 |
| `Init_Open_chest_object` | Initialize method of Open chest object. | 1065 |
| `Draw_Open_chest_object` | Draw method of Open chest object. | 1169 |
| `Restore_Open_chest_object` | Restore method of Open chest object. | 1231 |
| `Left_Chest_item_slot_object` | Left method of Chest item slot object. | 1302 |
| `DLeft_Chest_item_slot_object` | DLeft method of Chest item slot object. | 1372 |
| `Drop_Chest_item_slot_object` | Drop method of Chest item slot object. | 1423 |
| `Drag_chest_item` | Drag chest items. | 1466 |
| `Drop_on_chest_item` | Drop on chest item. | 1526 |
| `Chest_item_drag_abort_handler` | Chest item drag & drop abort handler. | 1695 |
| `Chest_item_PUM_evaluator` | Evaluate chest item pop-up menu. | 1748 |
| `PUM_Drop_chest_item` | Drop an chest item (chest item pop-up menu). | 1798 |
| `PUM_Examine_chest_item` | Examine an chest item (chest item pop-up menu). | 1859 |
| `Drop_chest_items` | Drop chest items. | 1899 |
| `Take_item_from_chest` | Take an item out of a chest. | 1967 |
| `Do_take_item_from_chest` | Event action: take an item from a chest. **R** | 2042 |
| `Put_item_in_chest` | Put an item in a chest. | 2108 |
| `Do_put_item_in_chest` | Event action: put an item into a chest. **R** | 2162 |
| `Auto_move_packet_to_chest` | Automatically move an item packet to a chest. | 2238 |
| `Move_drag_HDOB_towards_chest_slot` | Move drag HDOB towards a slot of a chest. | 2378 |

### DIAGNOST.C

`src/ALBION/SRC/DIAGNOST.C` – Diagnose- und Testfunktionen für Entwickler (Diagnosetasten, Ausgabe auf Diagnoseschirm, FLIC-Aufnahme).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Check_low_level_diagnostic_keys` | Check low-level diagnostic keys. | 109 |
| `Check_high_level_diagnostic_keys` | Check high-level diagnostic keys. | 261 |
| `Init_dprint` | Initialize a diagnostic "screen". | 498 |
| `Exit_dprint` | Destroy the current diagnostic "screen". | 560 |
| `Clrhome_dprint` | Erase the current diagnostic "screen" and reset the cursor. | 601 |
| `CR_dprint` | "Print" a carriage return on the current diagnostic "screen". | 629 |
| `Set_ink_dprint` | Set diagnostic ink. | 661 |
| `dprintf` | Print a string, using a printf-like format, on the current diagnostic "screen". | 691 |
| `MEM_List` | List the current status of the memory manager. | 729 |
| `MEM_Short_list` | Display a short list of the current status of the memory manager. | 866 |
| `MEM_Report` | List the current status of the memory manager. | 938 |
| `Save_screen` | Save the current screen. | 1078 |
| `Display_modifications` | List all map modifications for one map (diagnostic output). **R** *(aus)* | 1226 |
| `Start_flic_recording` | Allocate frame buffers and start recording the screen as a FLIC file. **R** *(aus)* | 1295 |
| `Stop_flic_recording` | Finish the FLIC recording and free its buffers. **R** *(aus)* | 1348 |
| `Urgle` | Play back the last recorded FLIC file (test function). **R** *(aus)* | 1381 |
| `Record_flic_frame` | Add the current screen to the FLIC recording. **R** *(aus)* | 1424 |

### DIALOGUE.C

`src/ALBION/SRC/DIALOGUE.C` – Gespräche mit Figuren: Gesprächsfenster, Wortliste, Themen, Gesprächsprotokoll, Aktionen im Gespräch.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Do_Dialogue` | Start a dialogue. | 384 |
| `Dialogue_ModInit` | Initialize Dialogue module. | 428 |
| `Dialogue_ModExit` | Exit Dialogue module. | 620 |
| `Dialogue_DisInit` | Initialize Dialogue display. | 686 |
| `Dialogue_DisExit` | Exit Dialogue display. | 729 |
| `Dialogue_MainLoop` | Main loop of Dialogue module. | 757 |
| `Init_dialogue_data` | Init dialogue data. | 1029 |
| `Exit_dialogue_data` | Exit dialogue data. | 1219 |
| `Draw_dialogue_screen` | Draw dialogue screen. | 1267 |
| `Handle_normal_MC_entry` | Handle a normal dialogue multiple-choice entry. | 1549 |
| `Handle_FAQ_MC_entry` | Handle a FAQ dialogue multiple-choice entry. | 1598 |
| `Handle_default_MC_entry` | Handle a default dialogue multiple-choice entry. | 1651 |
| `Handle_ask_word_default_MC_entry` | Handle the Ask Word default dialogue multiple-choice entry. | 1717 |
| `Handle_give_item_default_MC_entry` | Handle the Give Item default dialogue multiple-choice entry. | 1886 |
| `Do_give_item` | Event action: give an item to the dialogue partner. **R** | 1989 |
| `Handle_join_party_default_MC_entry` | Handle the Join Party default dialogue multiple-choice entry. | 2026 |
| `Do_join_party` | Event action: the dialogue partner joins the party. **R** | 2083 |
| `Handle_leave_party_default_MC_entry` | Handle the Leave Party default dialogue multiple-choice entry. | 2117 |
| `Do_leave_party` | Event action: the dialogue partner leaves the party. **R** | 2170 |
| `Handle_end_dialogue_default_MC_entry` | Handle the End Dialogue default dialogue multiple-choice entry. | 2197 |
| `Do_end_dialogue` | Event action: end the current dialogue. **R** | 2253 |
| `Set_current_dialogue_node` | Set current dialogue node. | 2281 |
| `Set_default_dialogue_node` | Set default dialogue node. | 2312 |
| `Set_standard_MC_entry_text_block` | Set standard MC entry text block. | 2343 |
| `Add_normal_MC_entries` | Add normal multiple-choice entries to a list. | 2373 |
| `Add_some_default_MC_entries` | Add some default multiple-choice entries to a list, depending on dialogue node data. | 2445 |
| `Add_FAQ_MC_entries` | Add FAQ multiple-choice entries to a list. | 2504 |
| `Add_default_MC_entries` | Add default multiple-choice entries to the global list. | 2616 |
| `Select_multiple_choice` | Select an answer from a set of multiple-choice options. | 2720 |
| `Init_MC_window_object` | Initialize method of Multiple-choice window object. | 2771 |
| `Draw_MC_window_object` | Draw method of Multiple-choice window object. | 2944 |
| `Init_MC_entry_object` | Initialize method of Multiple-choice entry object. | 2975 |
| `Draw_MC_entry_object` | Draw method of Multiple-choice entry object. | 3011 |
| `Feedback_MC_entry_object` | Feedback method of Multiple-choice entry object. | 3051 |
| `Highlight_MC_entry_object` | Highlight method of Multiple-choice entry object. | 3093 |
| `Left_MC_entry_object` | Left method of Multiple-choice entry object. | 3135 |
| `Draw_MC_entry` | Draw a multiple-choice entry. | 3174 |
| `Dialogue_error` | Report a dialogue error. | 3252 |
| `Dialogue_print_error` | Print a dialogue error. | 3280 |
| `Restore_dialogue_background` | Restore the background of the dialogue text window. | 3319 |
| `Display_text_in_dialogue` | Display a text block from a text file in the dialogue text window. | 3356 |
| `Init_dialogue_log` | Initialize dialogue log. | 3407 |
| `Exit_dialogue_log` | Exit dialogue log. | 3506 |
| `Destroy_dialogue_log_list` | Free a chain of dialogue log lists. **R** | 3523 |
| `Prepare_dialogue_log_for_saving` | Prepare the dialogue log for saving. | 3561 |
| `Add_dialogue_log_entry` | Add a new dialogue log entry to the list. | 3643 |
| `Find_dialogue_log_entry` | Find a dialogue log entry in the list. | 3745 |

### DOOR.C

`src/ALBION/SRC/DOOR.C` – Verschlossene Türen: Schloss knacken, Schlüssel benutzen, Fallen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Do_Door` | Enter Door screen. | 193 |
| `Door_ModInit` | Initialize Door module. | 257 |
| `Door_ModExit` | Exit Door module. | 316 |
| `Door_DisInit` | Initialize Door display. | 343 |
| `Door_DisExit` | Exit Door display. | 375 |
| `Door_MainLoop` | Main loop of Door module. | 405 |
| `Exit_Door` | Leave the door screen. | 472 |
| `Init_Door_object` | Initialize method of Door object. | 497 |
| `Draw_Door_object` | Draw method of Door object. | 542 |
| `Restore_Door_object` | Restore method of Door object. | 593 |
| `Init_Lock_object` | Init method of Lock display object. | 653 |
| `Draw_Lock_object` | Draw method of Lock display object. | 693 |
| `Feedback_Lock_object` | Feedback method of Lock display object. | 742 |
| `Help_Lock_object` | Help method of Lock display object. | 791 |
| `Drop_Lock_object` | Drop method of Lock display object. | 819 |
| `Inquire_drop_Lock_object` | Drop method of Lock object. | 965 |
| `Pop_up_Lock_object` | Pop-up method of Lock display object. | 1010 |
| `PUM_Pick_lock` | Pick the lock (lock pop-up menu). | 1041 |

### EVELOGIC.C

`src/ALBION/SRC/EVELOGIC.C` – Ereignislogik: löst Ereignisketten aus (Karte, Gegenstand, Magie, Gespräch) und führt Ereignisaktionen aus.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Perform_dialogue_action` | Perform an event-invoking action in a dialogue. | 187 |
| `Perform_action` | Perform an event-invoking action. | 221 |
| `Execute_event_action` | Execute the current event action. | 291 |
| `Handle_default_set` | Handle the default event set. | 388 |
| `Handle_map_set` | Handle action events from the map. | 446 |
| `Handle_item_set` | Handle the item event set. | 846 |
| `Handle_magic_set` | Handle the magic event set. | 894 |
| `Handle_dialogue_set` | Handle the dialogue partner's event set. | 942 |
| `Handle_acting_member_set` | Handle the acting (NOT acTIVE!!!) member's event set. | 1006 |
| `Handle_non_acting_member_set` | Handle a non-acting member's event set. | 1053 |
| `Handle_acting_part_set` | Handle the acting participant's event set. | 1102 |
| `Handle_friend_part_set` | Handle the event set of a friend of the acting participant. | 1160 |
| `Handle_enemy_part_set` | Handle the event set of an enemy of the acting participant. | 1238 |
| `Search_member_sets` | Search a party member's event sets. | 1308 |
| `Search_monster_sets` | Search a monster's event sets. | 1379 |
| `Prepare_event_set_context` | Prepare an event set context. | 1407 |
| `Search_event_set` | Search an event set for a certain action event. | 1470 |
| `Push_event_action` | Push a new event action on the stack. | 1607 |
| `Pop_event_action` | Pop an event action from the stack. | 1645 |
| `Reset_event_action` | Reset the event action stack. | 1674 |
| `Execute_event_chain` | Execute the current event chain (the one on the event context stack). | 1718 |
| `Chain_to_next_event` | Follow the chain to the next event in the current event chain. | 1807 |
| `Push_event_context` | Push a new event context on the stack. | 1886 |
| `Pop_event_context` | Pop an event context from the stack. | 1923 |
| `Reset_event_context` | Reset the event context stack. | 1966 |
| `Break_current_context` | Break the current event context. | 1995 |
| `Set_success_flag` | Set the success flag for the current context. | 2025 |
| `Clear_success_flag` | Clear the success flag for the current context. | 2055 |
| `Save_current_event` | Save the current event chain. | 2085 |
| `Event_is_saved` | Check if an event is saved. | 2126 |
| `Trigger_map_event_chain` | Try to trigger an event chain in the current map. | 2171 |
| `Trigger_NPC_event_chain` | Try to trigger an event chain for an NPC in the current map. | 2232 |
| `Search_triggered_event` | Search for an event chain in the current map with a certain trigger mode. | 2315 |
| `Search_triggered_NPC_event` | Search for an event chain in the current map with a certain trigger mode. | 2363 |
| `Search_triggered_map_event` | Search for an event chain in the current map with a certain trigger mode. | 2440 |
| `Get_event_triggers` | Get the event triggers of a position in the current map. | 2556 |
| `Get_NPC_event_triggers` | Get the event triggers of NPC's for a position in the current map. | 2597 |
| `Get_map_event_triggers` | Get the event triggers of a position in the current map. | 2700 |
| `Execute_chains_in_map` | Search the current map for event chains which have a given trigger-mode and execute these chains. | 2810 |
| `Execute_catalogued_chains_in_map` | Execute catalogued event chains in the current map. | 3003 |
| `Catalogue_event_chains` | Catalogue all event chains of a certain type in the current map. | 3157 |
| `Catalogue_chains_in_map` | Search the current map for event chains which have a given trigger-mode and catalogue these chains. | 3220 |
| `Destroy_event_chain_catalogues` | Destroy all event chain catalogues of the current map. | 3294 |
| `Update_event_chain_catalogues` | Update all event chain catalogues of the current map. | 3332 |
| `Map_context_validator` | Determine if a map event context is still valid. | 3367 |
| `Dialogue_context_validator` | Determine if the dialogue partner event context is still valid. | 3392 |
| `Party_member_context_validator` | Determine if a party member's event context is still valid. | 3444 |
| `Get_event_first_block_nr` | Get the number of the first block of a map event chain. | 3513 |
| `Get_event_chain_nr` | Get the number of an event chain. | 3557 |
| `Get_event_entry_at_position` | Get the event entry at a certain position in a map. | 3610 |
| `Get_event_chain_nr_at_position` | Get the event chain number at a certain position in a map. | 3674 |
| `Event_error` | Report an event error. | 3713 |
| `Display_event_data` | Print the data of an event and its context (diagnostic output). **R** | 3753 |

### EVENTS.C

`src/ALBION/SRC/EVENTS.C` – Behandler der einzelnen Ereignistypen (Kartenausgang, Tür, Truhe, Text, Falle, Ton, Szene …).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Map_Exit_event` | Map Exit event handler. | 160 |
| `Do_map_exit` | Do a map exit. | 345 |
| `Door_event` | Door event handler. | 432 |
| `Chest_event` | Chest event handler. | 514 |
| `Text_event` | Text event handler. | 606 |
| `Spinner_event` | Spinner event handler. | 927 |
| `Trap_event` | Trap event handler. | 1046 |
| `Do_trap` | Actually execute a trap. | 1133 |
| `Change_Icon_event` | Change Icon event handler. | 1192 |
| `Encounter_event` | Encounter event handler. | 1297 |
| `Place_action_event` | Place Action event handler. | 1381 |
| `Signal_event` | Signal event handler. | 1406 |
| `Clone_Automap_event` | Clone Automap event handler. | 1502 |
| `Sound_event` | Sound event handler. | 1713 |
| `Start_Dialogue_event` | Start Dialogue event handler. | 1830 |
| `Create_Trans_event` | Create Transport event handler. | 1879 |
| `Execute_event` | Execute event handler. | 1933 |
| `Remove_Member_event` | Remove Member event handler. | 1987 |
| `End_Dialogue_event` | End Dialogue event handler. | 2088 |
| `Wipe_event` | Wipe event handler. | 2113 |
| `Play_Animation_event` | Play Animation event handler. | 2143 |
| `Offset_event` | Offset event handler. | 2221 |
| `Pause_event` | Pause event handler. | 2286 |
| `Single_Item_Chest_event` | Single Item Chest event handler. | 2337 |
| `Do_Script_event` | Do Script event handler. | 2498 |

### EXAMITEM.C

`src/ALBION/SRC/EXAMITEM.C` – Fenster „Gegenstand untersuchen“ mit Werten und Beschreibung.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Examine_item` | Examine an item. | 165 |
| `Init_ExamItem1_object` | Initialize method of Examine item 1 window object. | 212 |
| `Draw_ExamItem1_object` | Draw method of Examine item 1 window object. | 300 |
| `ExamItem1_Exit` | Exit Examine item 1 window (button). | 569 |
| `Go_ExamItem2` | Enter Examine item 2 window (button). | 593 |
| `Init_ExamItem2_object` | Initialize method of Examine item 2 window object. | 647 |
| `Draw_ExamItem2_object` | Draw method of Examine item 2 window object. | 745 |
| `ExamItem2_Exit` | Exit Examine item 2 window (button). | 1073 |

### GAME.C

`src/ALBION/SRC/GAME.C` – Spielrahmen: BBMAIN, INI-Einstellungen, Bildschirm öffnen/schließen, Hauptschleife und Programmende.

| Funktion | Zweck | Zeile |
|---|---|---|
| `BBMAIN` | Main function of Albion | 193 |
| `Start_lengthy_memory_operation` | Indicate the start of a lengthy memory operation. | 423 |
| `End_lengthy_memory_operation` | Indicate the end of a lengthy memory operation. | 449 |
| `Exit_program` | Leave the program. | 473 |
| `Get_INI_variables` | Get variables from INI file. | 501 |
| `Init_screen` | Initialize the screen. | 589 |
| `Exit_screen` | Close the screen. | 775 |
| `Determine_screen_size` | Determine the size-based screen parameters. | 813 |
| `Open_screen` | Open the screen. | 859 |
| `Close_screen` | Close the screen. | 929 |
| `Init_sound` | Initialize sound. | 954 |
| `Report_error` | Report an error. | 1034 |
| `Print_error` | Print an error. | 1083 |

### GAMETEXT.C

`src/ALBION/SRC/GAMETEXT.C` – Spieltexte: Textdateien laden, Textblöcke finden, Wörterbuch, Textbefehle (HLC_…), die Namen, Pronomen, Preise usw. einsetzen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_game_texts` | Initialize game texts. | 312 |
| `Exit_game_texts` | Exit game texts. | 359 |
| `Find_text_block` | Find a (compiled) text block in a text file. | 398 |
| `Convert_text_file` | Scan a text file and divide into text blocks. | 460 |
| `Relocate_system_texts` | Relocate the system texts. *(aus)* | 560 |
| `Build_subblock_catalogue` | Scan a text block and build a catalogue of sub-blocks. | 611 |
| `Init_dictionary` | Initialize the dictionary. | 696 |
| `Exit_dictionary` | Exit the dictionary. | 762 |
| `Find_word_in_dictionary` | Find a word in a dictionary. | 792 |
| `Get_merged_word_index` | Get the index of a word in the merged dictionary. | 846 |
| `Search_word_in_dictionary` | Search a word in a dictionary. | 879 |
| `Search_references_to_merged_word` | Search all the references to a word in the merged dictionary. | 950 |
| `Merge_dictionary` | Add a dictionary to the merged dictionary. | 1003 |
| `Add_word_to_merged_dictionary` | Add a word to the merged dictionary. | 1059 |
| `Select_word` | Select a word from all known dictionary words. | 1144 |
| `Init_Word_window_object` | Init method of Word Window object. | 1185 |
| `Exit_Word_window_object` | Exit method of Word Window object. | 1369 |
| `Draw_Word_window_object` | Draw method of Word Window object. | 1400 |
| `Customkeys_Word_window_object` | Custom keys method of Word_window object. | 1451 |
| `Build_word_list` | Build a list containing all known dictionary words. | 1544 |
| `Swap_words` | Swap two words (for sorting). | 1632 |
| `Compare_words` | Compare two words (for sorting). | 1682 |
| `Update_word_list` | Update the word list (scroll bar function). | 1780 |
| `Word_input` | Enter a word (button). | 1827 |
| `Init_Word_object` | Init method of Word object. | 1886 |
| `Draw_Word_object` | Draw method of Word object. | 1920 |
| `Feedback_Word_object` | Feedback method of Word object. | 1961 |
| `Highlight_Word_object` | Highlight method of Word object. | 2004 |
| `Left_Word_object` | Left method of Word object. | 2047 |
| `Draw_word` | Draw Word object. | 2107 |
| `HLC_Unknown_word` | High level text commands. | 2188 |
| `HLC_Price` | Text command: insert the current place price. **R** | 2207 |
| `HLC_Damage` | Text command: insert the current combat damage. **R** | 2235 |
| `HLC_Weapon` | Text command: insert the name of the current combat weapon. **R** | 2262 |
| `HLC_Select_leader` | Text command: select the active character as subject. **R** | 2290 |
| `HLC_Select_self` | Text command: select the first party member as subject. **R** | 2311 |
| `HLC_Select_inventory` | Text command: select the inventory character as subject. **R** | 2332 |
| `HLC_Select_dialogue` | Text command: select the dialogue partner as subject. **R** | 2353 |
| `HLC_Select_combat` | Text command: select the acting combat participant as subject. **R** | 2374 |
| `HLC_Select_victim` | Text command: select the victim of the acting combat participant. **R** | 2399 |
| `HLC_Select_PUM_char` | Text command: select the character of the current pop-up menu. **R** | 2423 |
| `HLC_Select_subject_char` | Text command: select the current subject character. **R** | 2444 |
| `HLC_Name` | Text command: insert the name of the subject. **R** | 2465 |
| `HLC_He` | Text command: insert he/she/it for the subject. **R** | 2486 |
| `HLC_Him` | Text command: insert him/her/it for the subject. **R** | 2526 |
| `HLC_Him2` | Text command HIM2: insert a second form of him/her/it for the subject (only in the released MAIN.EXE, not in the 1995 source snapshots). **R** | 2567 |
| `HLC_His` | Text command: insert his/her/its for the subject. **R** | 2608 |
| `HLC_Man` | Text command: insert man/woman for the subject. **R** | 2648 |
| `HLC_Race` | Text command: insert the race of the subject. **R** | 2688 |
| `HLC_Class` | Text command: insert the class of the subject. **R** | 2706 |
| `HLC_Race_insult` | Text command: insert an insult for the race of the subject. **R** | 2724 |
| `HLC_Class_insult` | Text command: insert an insult for the class of the subject. **R** | 2742 |
| `HLC_Sex_char` | Text command: insert the sex symbol of the subject. **R** | 2760 |
| `HLC_Add_new_word` | Text command: add the given words to the party's dictionary. **R** | 2798 |
| `Gametext_error` | Report a gametext error. | 2876 |

### GAMETIME.C

`src/ALBION/SRC/GAMETIME.C` – Spielzeit: Schritte, Stunden, Tage, Warten; was zu jeder vollen Stunde und jedem Tag passiert.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_time` | Initialize time. | 69 |
| `Reset_time` | Reset time. | 110 |
| `Update_time` | Update time. | 145 |
| `Next_step` | Next step logic. | 180 |
| `Wait_x_hours` | Wait a number of hours. | 235 |
| `Next_hour` | Next hour logic. | 305 |
| `Next_day` | Next day logic. | 376 |
| `Next_month` | Next month logic. | 414 |
| `Next_year` | Next year logic. | 449 |

### GOLDFOOD.C

`src/ALBION/SRC/GOLDFOOD.C` – Anzeige und Handhabung von Gold und Rationen (Aufteilen, Wegwerfen, Weitergeben).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_Gold_food_object` | Init method of Gold/food object. | 159 |
| `Draw_Gold_food_object` | Draw method of Gold/food object. | 211 |
| `Update_Gold_food_object` | Update method of Gold/food object. | 256 |
| `Feedback_Gold_food_object` | Feedback method of Gold/food object. | 322 |
| `Highlight_Gold_food_object` | Highlight method of Gold/food object. | 367 |
| `Help_Gold_food_object` | Help method of Gold/food object. | 421 |
| `Pop_up_Gold_food_object` | Pop-up method of Gold/food object. | 470 |
| `Left_Gold_food_object` | Left method of Gold/food object. | 520 |
| `DLeft_Gold_food_object` | DLeft method of Gold/food object. | 606 |
| `Drop_Gold_food_object` | Drop method of Gold/food object. | 650 |
| `Inquire_drop_Gold_food_object` | Inquire drop method of Gold/food object. | 683 |
| `Drag_gold_food` | Drag gold or food. | 748 |
| `Drop_on_gold_food` | Drop on gold or food. | 830 |
| `Gold_food_drag_abort_handler` | Gold or food drag & drop abort handler. | 890 |
| `Draw_gold_food` | Draw Gold/food object. | 949 |
| `Get_gold_food_value` | Get the value out of a gold/food object. | 1024 |
| `Set_gold_food_value` | Set the value of a gold/food object. | 1134 |
| `Gold_food_PUM_evaluator` | Evaluate gold/food object pop-up menu. | 1239 |
| `PUM_Drop_gold_food` | Drop gold or food (gold/food object pop-up menu). | 1275 |
| `Show_dropping_gold_food` | Show dropping of gold / food. | 1387 |
| `Build_gold_food_graphics` | Build gold / food graphics for dragging. | 1481 |

### GRAPHICS.C

`src/ALBION/SRC/GRAPHICS.C` – Fest einkompilierte Grafiken (Symbole, Mauszeiger, Rahmen) als Datentabellen.

Keine Funktionen (nur Daten).

### INVENTO.C

`src/ALBION/SRC/INVENTO.C` – Inventarbildschirm: Wechsel zwischen Gruppenmitgliedern und Ansichten (Körper, Werte, Fähigkeiten).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Go_Inventory` | Go to a party member's inventory. | 232 |
| `Do_go_inventory` | Event action: enter (or switch) the inventory of a party member. **R** | 273 |
| `Exit_Inventory` | Leave the inventory screen (button function). | 342 |
| `Go_inventory_mode` | Go to a mode of a party member's inventory. | 393 |
| `Switch_inventory_mode` | Switch to mode of a party member's inventory (radio button). | 475 |
| `Inventory_ModInit` | Initialize Inventory module. | 499 |
| `Inventory_ModExit` | Exit Inventory module. | 537 |
| `Inventory_DisInit` | Initialize Inventory display. | 565 |
| `Inventory_DisExit` | Exit Inventory display. | 649 |
| `Init_inventory_data` | Init inventory data. | 675 |
| `Exit_inventory_data` | Exit inventory data. | 720 |
| `Init_InvRight_object` | Initialize method of Right Inventory object. | 746 |
| `Draw_InvRight_object` | Draw method of Right Inventory object. | 915 |
| `Init_Damage_display_object` | Init method of Damage display object. | 993 |
| `Draw_Damage_display_object` | Draw method of Damage display object. | 1025 |
| `Update_Damage_display_object` | Update method of Damage display object. | 1092 |
| `Help_Damage_display_object` | Help method of Damage display object. | 1151 |
| `Init_Protection_display_object` | Init method of Protection display object. | 1190 |
| `Draw_Protection_display_object` | Draw method of Protection display object. | 1222 |
| `Update_Protection_display_object` | Update method of Protection display object. | 1289 |
| `Help_Protection_display_object` | Help method of Protection display object. | 1348 |
| `Init_Weight_display_object` | Init method of Weight display object. | 1387 |
| `Draw_Weight_display_object` | Draw method of Weight display object. | 1420 |
| `Update_Weight_display_object` | Update method of Weight display object. | 1493 |
| `Help_Weight_display_object` | Help method of Weight display object. | 1570 |
| `Init_Party_gold_display_object` | Init method of party gold display object. | 1613 |
| `Draw_Party_gold_display_object` | Draw method of party gold display object. | 1645 |
| `Update_Party_gold_display_object` | Update method of party gold display object. | 1731 |
| `Help_Party_gold_display_object` | Help method of party gold display object. | 1786 |

### INVITEMS.C

`src/ALBION/SRC/INVITEMS.C` – Gegenstände im Inventar: Körperplätze und Rucksack, Ziehen und Ablegen, Anlegen und Ablegen von Ausrüstung.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_Body_item_list_object` | Initialize method of Body item list object. | 309 |
| `Draw_Body_item_list_object` | Draw method of Body item list object. | 375 |
| `Draw_Body_item_slot_object` | Draw method of Body item slot object. | 431 |
| `Feedback_Body_item_slot_object` | Feedback method of Body item slot object. | 476 |
| `Highlight_Body_item_slot_object` | Highlight method of Body item slot object. | 521 |
| `Left_Body_item_slot_object` | Left method of Body item slot object. | 566 |
| `Drop_Body_item_slot_object` | Drop method of Body item slot AND list object. | 620 |
| `Inquire_drop_item_slot_object` | Inquire drop method of Body and Backpack item slot AND Body item list object. | 654 |
| `Drag_body_item` | Drag a body item. | 702 |
| `Drop_on_body_item` | Drop on a body item. | 767 |
| `Erase_body_item_slot` | Erase a body item slot. | 942 |
| `Draw_body_item_slot_item` | Draw the item of a body item slot object. | 999 |
| `Left_Backpack_item_slot_object` | Left method of Backpack item slot object. | 1083 |
| `DLeft_Backpack_item_slot_object` | DLeft method of Backpack item slot object. | 1166 |
| `Drop_Backpack_item_slot_object` | Drop method of Backpack item slot object. | 1217 |
| `Drag_backpack_item` | Drag backpack items. | 1253 |
| `Drop_on_backpack_item` | Drop on backpack item. | 1327 |
| `Build_item_graphics` | Build item graphics for dragging. | 1543 |
| `Init_drag` | Initialize dragging HDOB & OPM. | 1611 |
| `Exit_drag` | Exit dragging. | 1674 |
| `Move_drag_HDOB_towards_char_slot` | Move drag HDOB towards a slot of a character's inventory. | 1706 |
| `Move_drag_HDOB_towards_object` | Move drag HDOB towards an object. | 1747 |
| `Body_backpack_item_drag_abort_handler` | Body & backpack item drag & drop abort handler. | 1814 |
| `Inventory_item_PUM_evaluator` | Evaluate inventory item pop-up menu. | 1905 |
| `PUM_Drop_inventory_item` | Drop an inventory item (inventory item pop-up menu). | 2193 |
| `PUM_Learn_spell_inventory_item` | Learn a spell from an inventory item (inventory item pop-up menu). | 2270 |
| `PUM_Examine_inventory_item` | Examine an inventory item (inventory item pop-up menu). | 2393 |
| `PUM_Use_inventory_item` | Use an inventory item (inventory item pop-up menu). | 2430 |
| `PUM_Drink_inventory_item` | Drink an inventory item (inventory item pop-up menu). | 2498 |
| `PUM_Activate_spell_inventory_item` | Activate a spell in an inventory item (inventory item pop-up menu). | 2582 |
| `PUM_Activate_inventory_item` | Activate an inventory item (inventory item pop-up menu). | 2622 |
| `PUM_Sell_inventory_item` | Sell an inventory item (inventory item pop-up menu). *((Merchant screen only))* | 2689 |
| `Drop_items` | Drop items. | 2825 |
| `Show_dropping_items` | Show dropping of items. | 2903 |
| `Do_use_item` | Use item event action. | 2988 |
| `Destroy_used_item` | Destroy a used item (if necessary). | 3015 |

### INVLEFT.C

`src/ALBION/SRC/INVLEFT.C` – Linke Inventarseite: Charakterwerte, Fähigkeiten und Zustände.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_InvLeft_object` | Initialize method of Left Inventory object. | 254 |
| `Init_InvLeft1_object` | Initialize method of Left Inventory 1 object. | 342 |
| `Update_InvLeft1_object` | Update method of Left Inventory 1 object. | 383 |
| `Draw_InvLeft1_object` | Draw method of Left Inventory 1 object. | 434 |
| `Init_InvLeft2_object` | Initialize method of Left Inventory 2 object. | 657 |
| `Draw_InvLeft2_object` | Draw method of Left Inventory 2 object. | 742 |
| `Init_InvLeft3_object` | Init method of Left Inventory 3 object. | 843 |
| `Update_InvLeft3_object` | Update method of Left Inventory 3 object. | 910 |
| `Draw_InvLeft3_object` | Draw method of Left Inventory 3 object. | 991 |
| `Init_Value_bar_object` | Init method of Value bar object. | 1202 |
| `Draw_Value_bar_object` | Draw method of Value bar object. | 1247 |
| `Update_Value_bar_object` | Update method of Value bar object. | 1356 |
| `Help_Value_bar_object` | Help method of Value bar object. | 1425 |
| `Attribute_value_getter` | Attribute value bars value getter. | 1485 |
| `Skill_value_getter` | Skill value bars value getter. | 1513 |

### ITMLOGIC.C

`src/ALBION/SRC/ITMLOGIC.C` – Gegenstandslogik: Gegenstände nehmen, geben, ablegen, anlegen, benutzen, Gewicht und Plätze.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_item_data` | Initialize item data. | 73 |
| `Exit_item_data` | Delete item data. | 137 |
| `Find_target_body_slot_for_item` | Find the target body slot for an item. | 168 |
| `Take_item_from_character` | Take an item out of a character's inventory. | 264 |
| `Do_take_item_from_char` | Event action: take an item from a character. **R** | 355 |
| `Put_item_in_character` | Put an item in a character's inventory. | 461 |
| `Do_put_item_in_char` | Event action: put an item into a character's inventory. **R** | 540 |
| `Remove_item` | Remove an item from a character's inventory. | 682 |
| `Add_item_to_body` | Add an item to a character's body items. | 753 |
| `Add_item_to_backpack` | Add an item to a character's backpack items. | 811 |
| `Auto_move_packet_to_backpack` | Automatically move an item packet to a character's backpack. | 878 |
| `Count_nr_items_that_will_fit_in_backpack` | Count the number of items of a certain type that will fit in a character's backpack. | 1022 |
| `Curse_item` | Curse an item in a character's inventory. | 1105 |
| `Decurse_item` | De-curse an item in a character's inventory. | 1155 |
| `Inventory_empty` | Check if an inventory is empty. | 1204 |
| `Inventory_full` | Check if an inventory is full. | 1242 |
| `Search_body_for_item_type` | Search all body items for an item of a certain type. | 1281 |
| `Remove_cursed_items` | Remove all cursed body items. | 1338 |
| `Has_cursed_items` | Check if a character has any cursed body items. | 1387 |
| `Free_item_slot_in_inventory` | Free an item slot in a character's inventory. | 1434 |
| `Free_item_slot_in_party` | Make sure there is a free slot somewhere in the party. | 1541 |
| `Optimise_inventory` | Try to optimise an inventory | 1659 |
| `Packet_empty` | Check if an item packet is empty. | 1771 |
| `Clear_packet` | Clear an item packet. | 1813 |
| `Get_item_data` | Get the item data of the item in an item packet. | 1838 |
| `Free_item_data` | Free item data after calling Get_item_data. | 1876 |
| `Get_item_name` | Get an item's name. | 1901 |
| `Build_item_packet` | Build an item packet. | 1942 |
| `Magical_item_evaluator` | Check if item is magical (item select window evaluator). | 1985 |
| `Vital_item_evaluator` | Check if item is vital for solving the game (item select window evaluator). | 2041 |
| `Show_moving_item` | Show an item moving from one position to another. | 2084 |
| `Show_moving_gold` | Show gold moving from one position to another. | 2140 |
| `Show_moving_food` | Show food moving from one position to another. | 2190 |

### MAGIC.C

`src/ALBION/SRC/MAGIC.C` – Magie außerhalb und innerhalb des Kampfes: Zauber wählen, Ziel bestimmen, Kosten, Wirkung auslösen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_magic_data` | Initialize magic data. | 397 |
| `Exit_magic_data` | Delete magic data. | 445 |
| `Cast_spell` | A party member casts a spell (NOT in combat). | 480 |
| `Do_cast_spell` | Event action: cast a spell through the handler list of its class. **R** | 569 |
| `Cast_combat_spell` | A party member casts a spell in combat. | 622 |
| `Do_cast_combat_spell` | A combat participant casts a spell in combat. | 714 |
| `Enter_spell_target` | Enter the target for the currently selected target. | 763 |
| `Select_a_tactical_square` | Select a (possibly empty) tactical square (combat spell target selection exception handler). | 1189 |
| `Select_row_of_tactical_squares` | Select a (possibly empty) row of tactical squares (combat spell target selection exception handler). | 1240 |
| `Select_blink_target` | Select targets for the blink spell (combat spell target selection exception handler). | 1299 |
| `Select_mega_killer_target` | Select victims for the mega killer spell (combat spell target selection exception handler). | 1383 |
| `Do_all_magic_party_targets` | Execute a spell on all targeted party members. | 1472 |
| `Do_all_magic_combat_targets` | Execute a spell on all targeted combat participants. | 1555 |
| `Get_magic_combat_part_target` | Get the targeted combat participant data. | 1698 |
| `Handle_spell` | Cast spell logic. | 1755 |
| `Remove_used_magic_item` | Remove used magic item. | 1871 |
| `Handle_magical_defense` | Handle the defense against a magical spell in combat. | 2017 |
| `Learn_spell` | Learn a new spell. | 2112 |
| `Improve_spell_strength` | Improve a spell's strength. | 2163 |
| `Calculate_required_LP` | Calculate the life-points (!) required to cast a spell. | 2215 |
| `Get_spell_area` | Return the current spell area type. | 2276 |
| `Update_temporary_spells` | Update temporary spells. | 2340 |
| `Update_temporary_spell` | Update a temporary spell. | 2378 |
| `Get_member_temporary_spell_strength` | Get the strength of a temporary spell for a party member. | 2415 |
| `Get_member_temporary_spell_duration` | Get the duration of a temporary spell for a party member. | 2454 |
| `Get_light_spell_strength` | Get the strength of the light temporary spell. | 2488 |
| `Set_member_temporary_spell` | Set the duration and strength of a temporary spell for a party member. | 2525 |
| `Set_light_spell` | Set the duration and strength of the light temporary spell. | 2566 |
| `Set_temporary_spell` | Set the duration and strength of a temporary spell. | 2593 |
| `Get_spell_targets` | Get a spell's targets. | 2632 |
| `Get_spell_areas` | Get the areas in which a spell can be cast. | 2672 |
| `Get_spell_required_SP` | Get the amount of SP required to cast a spell. | 2712 |
| `Get_spell_level` | Get a spell's level. | 2756 |
| `Get_spell_name` | Get a spell's name. | 2798 |
| `Select_spell` | Let the user select a spell. | 2833 |
| `Init_Spell_window_object` | Init method of Spell Window object. | 2989 |
| `Draw_Spell_window_object` | Draw method of Spell Window object. | 3141 |
| `Update_spell_list` | Update the spell list (scroll bar function). | 3187 |
| `Init_Spell_object` | Init method of Spell object. | 3231 |
| `Draw_Spell_object` | Draw method of Spell object. | 3265 |
| `Feedback_Spell_object` | Feedback method of Spell object. | 3305 |
| `Highlight_Spell_object` | Highlight method of Spell object. | 3347 |
| `Help_Spell_object` | Help method of Spell object. | 3403 |
| `Left_Spell_object` | Left method of Spell object. | 3489 |
| `Draw_spell` | Draw Spell object. | 3564 |
| `Spell_class_exists` | Check if a spell class exists. | 3711 |
| `Spell_exists` | Check if a spell exists. | 3757 |

### MAIN.C

`src/ALBION/SRC/MAIN.C` – Programmstart unter DOS: Fehlerprotokoll, Fehlerbehandlung, Programmargumente, Start und Ende des Soundsystems (AIL).

| Funktion | Zweck | Zeile |
|---|---|---|
| `main` | Main function of Albion | 267 |
| `Open_error_log` | Open the error log and print the error log header. | 465 |
| `Close_error_log` | Close the error log. | 509 |
| `Out_of_memory_handler` | Handle BBMEM out of memory error. | 548 |
| `Critical_error_handler` | Handle a critical error. | 594 |
| `OS_critical_error_handler` | Handle a critical OS error. | 624 |
| `Evaluate_program_arguments` | Evaluate program arguments. | 653 |
| `Main_init` | Initialize all libraries | 722 |
| `Main_exit` | Terminate all libraries | 878 |
| `Main_error_output_function` | Output function for BBERROR. | 918 |
| `Init_AIL_system` | Memory allocation function for AIL. | 952 |
| `Exit_AIL_system` | Shut down the sound system (empty in this version). **R** | 978 |
| `Local_Init_AIL_system` | Start AIL with BASEMEM allocation and register the BB32 system timer with AIL. **R** | 995 |
| `Local_Exit_AIL_system` | Stop and release the AIL timer, then shut AIL down. **R** | 1032 |
| `AIL_Alloc` | Memory allocator handed to AIL (flat BASEMEM block). **R** | 1060 |
| `AIL_Free` | Memory release handed to AIL (BASEMEM). **R** | 1077 |
| `My_system_timer` | AIL timer callback, runs the BB32 system timer function. **R** | 1096 |
| `Parse_argument` | Parse an argument. | 1127 |
| `Parse_value` | Parse a value. | 1167 |
| `Relocate_OPM` | Relocate a relocatable OPM. | 1198 |

### MAINMENU.C

`src/ALBION/SRC/MAINMENU.C` – Hauptmenü: neues Spiel, Laden, Speichern, Optionen, Ende.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Enter_Main_menu` | Enter Main menu screen. | 202 |
| `Main_menu_ModInit` | Initialize Main menu module. | 243 |
| `Main_menu_ModExit` | Exit Main menu module. | 285 |
| `Main_menu_DisInit` | Initialise Main menu display. | 328 |
| `Main_menu_DisExit` | Exit Main menu display. | 412 |
| `Main_menu_MainLoop` | Main loop of Main menu. | 460 |
| `Main_menu_PUM_evaluator` | Evaluate main menu pop-up menu. | 496 |
| `Main_menu_Start_new_game` | Start a new game (main menu pop-up menu). | 552 |
| `Main_menu_Continue_game` | Continue game (main menu pop-up menu). | 586 |
| `Main_menu_Load_game` | Load a saved game (main menu pop-up menu). | 672 |
| `Main_menu_Save_game` | Save game (main menu pop-up menu). | 735 |
| `Main_menu_Options` | Options (main menu pop-up menu). | 850 |
| `Main_menu_View_intro` | View intro (main menu pop-up menu). | 892 |
| `Main_menu_View_credits` | View credits (main menu pop-up menu). | 930 |
| `Main_menu_End_game` | End game (main menu pop-up menu). | 968 |
| `Build_list_of_saved_games` | Build a list of saved games. | 1016 |
| `Load_saved_game_evaluator` | Evaluator for loading saved games (select window). | 1181 |
| `Draw_saved_game` | Saved game draw function (select window). | 1230 |
| `Init_Options_object` | Initialize method of Options window object. | 1312 |
| `Exit_Options_object` | Exit method of Options window object. | 1476 |
| `Draw_Options_object` | Draw method of Options window object. | 1566 |
| `Customkeys_Options_object` | Customkey method of Options window object. | 1649 |
| `Options_Exit` | Exit Options window (button). | 1704 |

### MERCHANT.C

`src/ALBION/SRC/MERCHANT.C` – Händler: Kaufen und Verkaufen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Enter_Merchant` | Enter Merchant screen. | 175 |
| `Merchant_ModInit` | Initialize Merchant module. | 202 |
| `Merchant_ModExit` | Exit Merchant module. | 270 |
| `Merchant_DisInit` | Initialize Merchant display. | 305 |
| `Merchant_DisExit` | Exit Merchant display. | 337 |
| `Exit_Merchant` | Leave the Merchant screen. | 366 |
| `Init_Merchant_object` | Initialize method of Merchant object. | 392 |
| `Draw_Merchant_object` | Draw method of Merchant object. | 449 |
| `Help_Merchant_item_object` | Help method of merchant item object. | 501 |
| `Merchant_item_PUM_evaluator` | Evaluate Merchant item pop-up menu. | 585 |
| `PUM_Buy_merchant_item` | Buy a Merchant item (Merchant item pop-up menu). | 652 |
| `PUM_Examine_merchant_item` | Examine a Merchant item (Merchant item pop-up menu). | 809 |
| `Auto_move_packet_to_merchant_data` | Automatically move an item packet to the current merchant data. | 848 |
| `Count_nr_items_that_will_fit_in_merchant_data` | Count the number of items of a certain type that will fit in the current merchant data. | 955 |
| `Merchant_sell_requester` | Ask if the player wants to sell items. | 1013 |

### MUSIC.C

`src/ALBION/SRC/MUSIC.C` – Musik und Soundeffekte ein- und ausschalten, Lautstärken, ortsabhängige Effekte.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Sound_on` | Switch music and sound effects on. | 271 |
| `Sound_off` | Switch music and sound effects off. | 298 |
| `Music_on` | Switch music on. | 324 |
| `Music_off` | Switch music off. | 372 |
| `Sound_effects_on` | Switch sound effects on. | 421 |
| `Sound_effects_off` | Switch sound effects off. | 452 |
| `Located_sound_effects_on` | Switch located sound effects on. | 510 |
| `Located_sound_effects_off` | Switch located sound effects off. | 543 |
| `Get_MIDI_volume` | Get global MIDI music volume. | 589 |
| `Set_MIDI_volume` | Set global MIDI music volume. | 627 |
| `Get_digital_volume` | Get global digital sound volume. | 680 |
| `Set_digital_volume` | Set global digital sound volume. | 718 |
| `Init_sound_system` | Initialize sound system. | 750 |
| `Exit_sound_system` | Exit sound system. | 948 |
| `Update_sound_system` | Update music and sound effects. | 1072 |
| `Play_song` | Start playing a song. | 1119 |
| `Play_ambient_song` | Start playing an ambient song. | 1216 |
| `Play_jingle` | Play a jingle. | 1374 |
| `Play_sound_effect` | Play a sound effect. | 1468 |
| `Initialize_located_effects` | Initialize located sound effects. | 1600 |
| `Load_located_effects` | Load located sound effects. | 1693 |
| `Get_located_effect_table_address` | Get address of located sound effect table. | 1753 |
| `Get_located_effect_table_length` | Get length of located sound effect table. | 1777 |
| `Add_located_effect` | Add a located sound effect. | 1811 |
| `Remove_located_effect` | Remove a located sound effect. | 1930 |
| `Remove_located_effects_at` | Remove all located sound effects at a certain position. | 1965 |
| `Set_listener_position` | Set position of listener within effect space. | 2006 |
| `Set_effect_position` | Set position of located effect within effect space. | 2035 |
| `Music_error` | Report a music error. | 2070 |
| `Music_print_error` | Print a music error. | 2103 |
| `Pause_song` | Pause a playing song. | 2144 |
| `Continue_song` | Continue a paused song. | 2179 |
| `End_song` | End a song. | 2213 |
| `Update_sound_effects` | Check all normal and located and sound effects and allocate digital channels. | 2260 |
| `Swap_sound_effects` | Swap two sound effects (for sorting). | 2411 |
| `Compare_sound_effects` | Compare two sound effects (for sorting). | 2447 |
| `Update_located_sound_effects` | Determine if any located sound effects should be started. | 2487 |
| `Start_sound_effect` | Start playing a sound effect. | 2615 |
| `Update_sound_effect` | Update a playing sound effect. | 2736 |
| `Stop_sound_effect` | Stop playing a sound effect. | 2800 |
| `Delete_sound_effect` | Delete a sound effect. | 2849 |
| `Stop_all_digital_channels` | Stop all digital channels that are currently playing. | 2888 |
| `Stop_digital_channel` | Stop playing a digital channel. | 2919 |

### NPCS.C

`src/ALBION/SRC/NPCS.C` – Nicht-Spieler-Figuren auf 2D- und 3D-Karten: Laden, Bewegung auf Pfaden, Zufallsbewegung, Begegnungen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_NPC_data` | Initialize NPC data. | 128 |
| `Clean_up_NPC_path` | Scan an NPC path and remove illegal values. | 454 |
| `Init_2D_NPCs` | Initialize NPCs in a 2D map. | 498 |
| `Exit_2D_NPCs` | Exit NPCs in a 2D map. | 556 |
| `Init_2D_NPC_graphics` | Initialize NPC graphics in a 2D map. | 594 |
| `Exit_2D_NPC_graphics` | Exit NPC graphics in a 2D map. | 665 |
| `Init_3D_NPCs` | Initialize NPCs in a 3D map. | 690 |
| `Exit_3D_NPCs` | Exit NPCs in a 3D map. | 741 |
| `Handle_2D_NPCs` | Handle NPCs in a 2D map. | 766 |
| `Display_2D_NPCs` | Display NPCs in a 2D map. | 962 |
| `Do_path_NPC_2D` | Handle an NPC in a 2D map walking along a path. | 1106 |
| `Do_random_NPC_2D` | Handle an NPC in a 2D map moving randomly. | 1232 |
| `Do_waiting_NPC_2D` | Handle an NPC in a 2D map standing around. | 1308 |
| `Do_chasing_NPC_2D` | Handle an NPC in a 2D map chasing the party. | 1348 |
| `Try_chasing_NPC_2D_move` | Try moving a chasing NPC in a 2D map. | 1547 |
| `Do_locked_NPC_2D` | Handle a locked NPC in a 2D map (scripts only). | 1604 |
| `Handle_3D_NPCs` | Handle NPCs in a 3D map. | 1717 |
| `Display_3D_NPCs` | Display NPCs in a 3D map. | 1829 |
| `Update_path_NPC_3D` | Update the path of an NPC in a 3D map. | 1881 |
| `Handle_non_path_NPC_3D` | Update the position of an NPC in a 3D map not on a path. | 1964 |
| `Do_path_NPC_3D` | Handle an NPC in a 3D map walking along a path. | 2076 |
| `Do_random_NPC_3D` | Handle an NPC in a 3D map moving randomly. | 2145 |
| `Do_waiting_NPC_3D` | Handle an NPC in a 3D map standing around. | 2211 |
| `Do_chasing_NPC_3D` | Handle an NPC in a 3D map chasing the party. | 2234 |
| `Check_line_of_sight` | Check if the party is an NPC's line of sight. | 2437 |
| `Check_for_NPC_reaction` | Check for a reaction between NPC and party. | 2580 |
| `NPC_present` | Check if an NPC in the current map is present. *(aus)* | 2738 |
| `Search_2D_NPC` | Search for an NPC in the current 2D map. | 2781 |
| `Search_3D_NPC` | Search for an NPC in the current 3D map. | 2863 |
| `Choose_next_random_NPC_path` | Choose the next random path for an NPC. | 2912 |
| `Turn_towards_NPC` | Turn towards an NPC. | 2946 |
| `Get_target_VD` | Get target view direction when rotating in a 2D map. | 3133 |
| `Update_NPC_present_status` | Update the present flags of all NPCs in the current map. | 3216 |
| `Skip_through_NPC_paths` | Skip through NPC path data in a map data file. | 3312 |
| `Lock_NPC` | Lock an NPC. | 3396 |
| `Unlock_NPC` | Unlock an NPC. | 3428 |
| `Unlock_all_NPCs` | Unlock all NPCs. | 3457 |
| `Set_NPC_position` | Set the position of an NPC. | 3489 |
| `Move_locked_NPC` | Move a locked NPC (for scripts only). | 3531 |

### NPCSOUND.C

`src/ALBION/SRC/NPCSOUND.C` – Geräusche, die von Figuren auf der Karte ausgehen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Exit_NPC_sound_effects` | Exit NPC sound effects. | 197 |
| `Remove_all_NPC_sound_effects` | Remove all sound effects of an NPC. | 228 |
| `Update_NPC_sound_effects` | Update NPC sound effects. | 263 |
| `Add_NPC_sound_effect` | Add an NPC's sound effect. | 365 |
| `Remove_NPC_sound_effect` | Remove an NPC's sound effect. | 434 |
| `Get_NPC_effect_coordinates` | Get an NPC's sound effect coordinates. | 468 |

### PLACES.C

`src/ALBION/SRC/PLACES.C` – Orte mit Diensten: Ausbilden, Heilen, Zustände heilen, Gegenstände reparieren, Rasten gegen Bezahlung.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Do_place_action` | Execute a place action. | 178 |
| `Train_skill_place_handler` | Train skill place handler. | 239 |
| `Heal_LP_place_handler` | Heal LP place handler. | 388 |
| `Heal_LP_member_evaluator` | Check if a party member's LP can be healed (member select window evaluator). | 533 |
| `Heal_condition_place_handler` | Heal condition place handler. | 571 |
| `Heal_condition_member_evaluator` | Check if a party member's conditions can be healed (member select window evaluator). | 710 |
| `Heal_condition_evaluator` | Evaluator for healing conditions (select window). | 750 |
| `Draw_condition` | Heal condition draw function (select window). | 809 |
| `Remove_cursed_item_place_handler` | Remove cursed items place handler. | 841 |
| `Remove_cursed_item_member_evaluator` | Check if a party member carries any cursed items (member select window evaluator). | 911 |
| `Examine_item_place_handler` | Examine item place handler. | 949 |
| `Examine_item_evaluator` | Check if an item can be examined (item select window evaluator). | 1058 |
| `Recharge_item_place_handler` | Recharge item place handler. | 1097 |
| `Recharge_item_evaluator` | Check if an item can be recharged (item select window evaluator). | 1270 |
| `Rent_room_place_handler` | Rent room place handler. | 1328 |
| `Merchant_place_handler` | Merchant place handler. | 1383 |
| `Buy_food_place_handler` | Buy food place handler. | 1407 |
| `Buy_transport_place_handler` | Buy transport place handler. | 1514 |
| `Learn_spell_place_handler` | Learn spell place handler. | 1538 |
| `Learn_spell_evaluator` | Evaluator for learning spells (select window). | 1650 |
| `Draw_learn_spell` | Learn spell draw function (select window). | 1711 |
| `Repair_item_place_handler` | Repair item place handler. | 1754 |
| `Repair_item_evaluator` | Check if an item can be repaired (item select window evaluator). | 1864 |
| `Place_buy_requester` | Ask if the player wants to buy a place service. | 1905 |

### PRTLOGIC.C

`src/ALBION/SRC/PRTLOGIC.C` – Gruppen- und Charakterlogik: Spieldaten, Gruppenmitglieder, Werte, Schaden, Heilung, Erfahrung, Stufenaufstieg, Bitfelder.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_game_data` | Initialize game data. | 121 |
| `Exit_game_data` | Delete game data. | 182 |
| `Calculate_game_tables` | Calculate tables needed by the game. | 220 |
| `Init_party_data` | Initialize the party members' data. | 268 |
| `Exit_party_data` | Delete all party members' data. | 425 |
| `Clear_bit_array` | Clear a bit array. | 465 |
| `Read_bit_array` | Read a bit from a bit array. | 580 |
| `Write_bit_array` | Write a bit from a bit array. | 710 |
| `Select_new_active_member` | Select a new active party member. | 871 |
| `Game_over` | Game over. | 938 |
| `Activate_party_member` | Activate a party member. | 993 |
| `Do_activate_party_member` | Event action: make a party member the active character. **R** | 1077 |
| `Find_character_in_party` | Find a character in the party. | 1117 |
| `Find_char_data_in_party` | Find a character data in the party. | 1158 |
| `Character_alive` | Check if a character is alive. | 1200 |
| `Character_capable` | Check if a character is capable. | 1229 |
| `Party_can_see` | Check if the party can see. | 1258 |
| `Party_is_full` | Check if the party is full. | 1281 |
| `Character_has_magical_abilities` | Check if a character has magical abilities. | 1321 |
| `Character_knows_spells` | Check if a character knows any spells. | 1364 |
| `Character_is_overweight` | Check if a character is overweight. | 1413 |
| `Probe` | Probe a value. A random number between 0 and the probe range is determined. If this number is smaller or equal to the probe value, the probe was successful. | 1443 |
| `Probe_attribute` | Probe a character's attribute. | 1476 |
| `Probe_skill` | Probe a character's skill. | 1500 |
| `Get_rnd_50_100` | Get random value between 50% of 100% of input value. | 1523 |
| `Get_attribute` | Get a character's attribute. | 1547 |
| `Get_real_attribute` | Get a character's attribute, without including the effects of any equipped items. | 1625 |
| `Set_attribute` | Set a character's attribute. | 1665 |
| `Get_max_attribute` | Get a character's maximum attribute. | 1701 |
| `Set_max_attribute` | Set a character's maximum attribute. | 1741 |
| `Get_skill` | Get a character's skill. | 1777 |
| `Get_real_skill` | Get a character's skill, without including the effects of any equipped items. | 1878 |
| `Set_skill` | Set a character's skill. | 1918 |
| `Get_max_skill` | Get a character's maximum skill. | 1954 |
| `Set_max_skill` | Set a character's maximum skill. | 1994 |
| `Set_condition` | Set a character's body condition. | 2030 |
| `Clear_condition` | Clear a character's body condition. | 2082 |
| `Get_conditions` | Get a character's body conditions. | 2117 |
| `Get_char_name` | Get a character's name. | 2153 |
| `Get_class` | Get a character's class. | 2190 |
| `Get_level` | Get a character's level. | 2224 |
| `Get_sex` | Get a character's sex. | 2258 |
| `Get_race` | Get a character's race. | 2292 |
| `Get_known_languages` | Get a character's known languages list. | 2326 |
| `Get_character_type` | Get a character's type bitlist. | 2360 |
| `Get_LP` | Get a character's life points. | 2394 |
| `Set_LP` | Set a character's life points. | 2431 |
| `Get_max_LP` | Get a character's maximum life points. | 2462 |
| `Get_real_max_LP` | Get a character's maximum life points, without including the effects of any equipped items. | 2523 |
| `Set_max_LP` | Set a character's maximum life points. | 2560 |
| `Get_SP` | Get a character's spell points. | 2591 |
| `Set_SP` | Set a character's spell points. | 2626 |
| `Get_max_SP` | Get a character's maximum spell points. | 2657 |
| `Get_real_max_SP` | Get a character's maximum spell points, without including the effects of any equipped items. | 2718 |
| `Set_max_SP` | Set a character's maximum spell points. | 2753 |
| `Get_EP` | Get a character's experience points. | 2784 |
| `Set_EP` | Set a character's experience points. | 2819 |
| `Get_TP` | Get a character's training points. | 2853 |
| `Set_TP` | Set a character's training points. | 2888 |
| `Get_carried_weight` | Get the weight carried by a character. | 2919 |
| `Get_max_weight` | Get the maximum weight that can be carried by a character. | 2991 |
| `Get_nr_occupied_hands` | Get the number of occupied hands of a character. | 3019 |
| `Get_event_set_index` | Get the event set index of a character. | 3091 |
| `Set_event_set_index` | Set the event set index of a character. | 3130 |
| `Spell_class_known` | Check if a character knows a certain spell class. | 3166 |
| `Spell_known` | Check if a character knows a certain spell. | 3211 |
| `Get_spell_strength` | Get the strength of a certain spell of a character. | 3274 |
| `Set_spell_strength` | Get the strength of a certain spell of a character. | 3329 |
| `Get_damage` | Get the damage a character can do. | 3368 |
| `Get_protection` | Get the protection a character has. | 3421 |
| `Do_damage` | Do damage to a party member. | 3472 |
| `Show_party_member_damage` | Show party member receiving damage. | 3528 |
| `Kill_party_member` | "Kill" a party member. | 3563 |
| `Do_healing` | Heal a party member. | 3612 |
| `Show_party_member_healing` | Show party member healing. | 3665 |
| `Revive_party_member` | "Revive" a party member. | 3700 |
| `De_exhaust_party_member` | De-exhaust a party member. | 3737 |
| `Check_member_levels` | Check if any party member's should advance to the next level. | 3796 |
| `Increase_character_level` | Increase the level of a character. | 3875 |
| `Char_inventory_empty` | Check if a character's inventory is empty. | 4019 |
| `Char_inventory_full` | Check if a character's inventory is full. | 4055 |
| `Count_items_on_body` | Count all the items of a certain type on a character's body. | 4092 |
| `Count_items_in_backpack` | Count all the items of a certain type in a character's backpack. | 4137 |
| `Alive_member_evaluator` | Check if a party member is alive (member select window evaluator). | 4181 |
| `Can_be_active_member_evaluator` | Check if a party member can be active (member select window evaluator). | 4216 |
| `Healable_member_evaluator` | Check if a party member can be healed (member select window evaluator). | 4278 |
| `Remove_party_member` | Remove a party member from the party. | 4312 |
| `Add_party_member` | Add a party member to the party. | 4449 |
| `Get_party_gold` | Get the amount of gold coins carried by the party. | 4605 |
| `Set_party_gold` | Set the amount of gold coins carried by the party. | 4649 |
| `Get_party_food` | Get the amount of food rations carried by the party. | 4833 |
| `Set_party_food` | Set the amount of food rations carried by the party. | 4877 |
| `Count_party_members` | Count the number of party members. | 5062 |
| `Count_alive_party_members` | Count the number of party members who are alive. | 5101 |
| `Calculate_party_light` | Calculate the amount of light the party is generating because of light-giving items they are carrying. | 5145 |
| `Update_party_light` | Update the light-giving items the party is carrying. | 5267 |
| `Do_camp_logic` | Execute camp logic, warning the player for exhaustion or exhausting the party. | 5377 |
| `Do_poison_logic` | Execute poison logic, hurting all poisoned party members. | 5489 |
| `Do_diseased_logic` | Execute disease logic, decreasing a random attribute of all diseased party members. | 5533 |
| `Character_has_magical_items` | Search a character for magical items. | 5590 |
| `Member_present` | Check if a party member is present. | 5674 |
| `Customkeys_party` | "Custom keys method" for party short-cuts. | 5712 |

### QUERMOD.C

`src/ALBION/SRC/QUERMOD.C` – Ereignisse für Abfragen und Änderungen von Spieldaten (Bedingungen prüfen, Werte ändern).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Change_Used_Item_event` | Change Used Item event handler. | 197 |
| `Datachange_event` | Datachange event handler. | 347 |
| `Do_datachange` | Actually change data. | 626 |
| `Query_event` | Query event handler. | 1087 |
| `Query_compare` | Compare query value with given number. | 1893 |
| `Modify_event` | Modify event handler. | 1954 |
| `Modify_amount` | Modify an amount. | 2417 |
| `Is_modify_possible` | Check if a modification is possible. | 2512 |
| `Modify_amount_from_maximum` | Modify an amount, using the maximum value as a reference for relative modifications. | 2592 |
| `Modify_carried_items` | Modify the number of a certain item carried by a character. | 2690 |
| `Modify_items_carried_by_party` | Modify the number of a certain item carried by the party. | 2944 |

### SAVELOAD.C

`src/ALBION/SRC/SAVELOAD.C` – Spielstände: Laden, Speichern, Anfangszustand, Prüfung der gespeicherten XLD-Bibliotheken.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Select_saved_game` | Select a saved game. | 122 |
| `Load_initial_game_state` | Load initial game state. | 154 |
| `Load_game_state` | Load game state. | 265 |
| `Save_game_state` | Save game state. | 916 |
| `Init_saved_XLD_library_check` | Remember the subfile lengths of the saved XLD libraries for later checks. **R** | 1645 |
| `Check_saved_XLD_library` | Compare a loaded saved XLD library with the remembered subfile lengths and restore lengths that differ. **R** | 1749 |

### SCRIPT.C

`src/ALBION/SRC/SCRIPT.C` – Zwischensequenzen und Skripte („forced control“): Skriptzeilen auswerten und ausführen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Execute_script` | Execute a forced control script. | 366 |
| `Script_ModInit` | Initialize Script module. | 424 |
| `Script_MainLoop` | Script main loop. | 622 |
| `Script_DisUpd` | Update Script display. | 651 |
| `Analyse_script` | Analyse the lines of a forced control script. | 682 |
| `Read_numeric_argument` | Read a numeric argument from a script. | 875 |
| `Set_script_background_type` | Set the script background type. | 959 |
| `Party_jump_script_command_handler` | Party jump script command handler. | 1028 |
| `Party_move_script_command_handler` | Party move script command handler. | 1064 |
| `NPC_jump_script_command_handler` | NPC jump script command handler. | 1111 |
| `NPC_move_script_command_handler` | NPC move script command handler. | 1148 |
| `Show_map_script_command_handler` | Show map script command handler. | 1185 |
| `Do_event_chain_script_command_handler` | Do event chain script command handler. | 1221 |
| `Show_pic_script_command_handler` | Show picture script command handler. | 1279 |
| `Sound_script_command_handler` | Sound script command handler. | 1358 |
| `Song_script_command_handler` | Song script command handler. | 1406 |
| `Ambient_script_command_handler` | Ambient song script command handler. | 1439 |
| `Set_quest_bit_script_command_handler` | Set quest bit script command handler. | 1472 |
| `Clear_quest_bit_script_command_handler` | Clear quest bit script command handler. | 1505 |
| `NPC_on_script_command_handler` | NPC on script command handler. | 1538 |
| `NPC_off_script_command_handler` | NPC off script command handler. | 1575 |
| `Lock_NPC_script_command_handler` | Lock NPC script command handler. | 1612 |
| `Unlock_NPC_script_command_handler` | Unlock NPC script command handler. | 1645 |
| `Change_icon_script_command_handler` | Change icon script command handler. | 1678 |
| `Wipe_script_command_handler` | Wipe script command handler. | 1725 |
| `Play_anim_script_command_handler` | Play animation script command handler. | 1755 |
| `Text_script_command_handler` | Text script command handler. | 1806 |
| `Party_member_text_script_command_handler` | Party member text script command handler. | 1850 |
| `NPC_text_script_command_handler` | NPC text script command handler. | 1916 |
| `Active_member_text_script_command_handler` | Active member text script command handler. | 2000 |
| `Pause_script_command_handler` | Pause script command handler. | 2059 |
| `Fill_screen_script_command_handler` | Fill screen script command handler. | 2108 |
| `Start_anim_script_command_handler` | Start animation script command handler. | 2176 |
| `Play_script_command_handler` | Play frames of animation script command handler. | 2224 |
| `Stop_anim_script_command_handler` | Stop animation script command handler. | 2257 |
| `Load_pal_script_command_handler` | Load palette script command handler. | 2285 |
| `Turn_party_script_command_handler` | Turn party script command handler. | 2318 |
| `Turn_NPC_script_command_handler` | Turn NPC script command handler. | 2354 |
| `Lock_camera_script_command_handler` | Lock camera script command handler. | 2390 |
| `Unlock_camera_script_command_handler` | Unlock camera script command handler. | 2418 |
| `Camera_jump_script_command_handler` | Camera jump script command handler. | 2446 |
| `Camera_move_script_command_handler` | Camera move script command handler. | 2482 |
| `Update_script_command_handler` | Update script command handler. | 2527 |
| `Fade_to_black_script_command_handler` | Fade to black script command handler. | 2566 |
| `Fade_to_white_script_command_handler` | Fade to white script command handler. | 2594 |
| `Fade_from_black_script_command_handler` | Fade from black script command handler. | 2622 |
| `Fade_from_white_script_command_handler` | Fade from white script command handler. | 2650 |
| `Party_on_script_command_handler` | Party on script command handler. | 2678 |
| `Party_off_script_command_handler` | Party off script command handler. | 2706 |
| `Party_awaken_script_command_handler` | Party awaken script command handler. | 2734 |
| `Party_activate_script_command_handler` | Party activate script command handler. | 2779 |
| `Sound_effects_off_script_command_handler` | Sound effects off script command handler. | 2820 |
| `Script_error` | Report a script error. | 2847 |
| `Script_print_error` | Print a script error. | 2887 |
| `Play_animation` | Play an animation. | 2937 |
| `Start_animation` | Load and intialize an animation. | 2988 |
| `Play_animation_frames` | Play some frames of an animation. | 3200 |
| `Stop_animation` | Stop playing an animation. | 3292 |
| `Wipe` | Wipe the screen. | 3339 |

### SOUND.C

`src/ALBION/SRC/SOUND.C` – Zweite Fassung der Musik- und Soundsteuerung (Präfix SOUND_).

| Funktion | Zweck | Zeile |
|---|---|---|
| `SOUND_Sound_on` | Switch music and sound effects on. | 270 |
| `SOUND_Sound_off` | Switch music and sound effects off. | 297 |
| `SOUND_Music_on` | Switch music on. | 323 |
| `SOUND_Music_off` | Switch music off. | 361 |
| `SOUND_Sound_effects_on` | Switch sound effects on. | 399 |
| `SOUND_Sound_effects_off` | Switch sound effects off. | 430 |
| `SOUND_Located_sound_effects_on` | Switch located sound effects on. | 492 |
| `SOUND_Located_sound_effects_off` | Switch located sound effects off. | 525 |
| `SOUND_Get_MIDI_volume` | Get global MIDI music volume. | 571 |
| `SOUND_Set_MIDI_volume` | Set global MIDI music volume. | 598 |
| `SOUND_Get_digital_volume` | Get global digital sound volume. | 652 |
| `SOUND_Set_digital_volume` | Set global digital sound volume. | 678 |
| `SOUND_Init_sound_system` | Initialize sound system. | 715 |
| `SOUND_Exit_sound_system` | Exit sound system. | 970 |
| `SOUND_Update_sound_system` | Update music and sound effects. | 1087 |
| `SOUND_Play_song` | Start playing a song. | 1134 |
| `SOUND_Play_ambient_song` | Start playing an ambient song. | 1242 |
| `SOUND_Play_jingle` | Play a jingle. | 1387 |
| `SOUND_Play_sound_effect` | Play a sound effect. | 1485 |
| `SOUND_Initialize_located_effects` | Initialize located sound effects. | 1616 |
| `SOUND_Load_located_effects` | Load located sound effects. | 1709 |
| `SOUND_Get_located_effect_table_address` | Get address of located sound effect table. | 1769 |
| `SOUND_Get_located_effect_table_length` | Get length of located sound effect table. | 1793 |
| `SOUND_Add_located_effect` | Add a located sound effect. | 1824 |
| `SOUND_Remove_located_effect` | Remove a located sound effect. | 1942 |
| `SOUND_Remove_located_effects_at` | Remove all located sound effects at a certain position. | 1977 |
| `SOUND_Set_listener_position` | Set position of listener within effect space. | 2018 |
| `SOUND_Set_effect_position` | Set position of located effect within effect space. | 2047 |
| `SOUND_Error` | Report a sound system error. | 2083 |
| `SOUND_Print_error` | Print a sound system error. | 2116 |
| `SOUND_Pause_song` | SOUND_Pause a playing song. | 2158 |
| `SOUND_Continue_song` | Continue a paused song. | 2193 |
| `SOUND_End_song` | End a song. | 2227 |
| `SOUND_Update_sound_effects` | Check all normal and located and sound effects and allocate digital channels. | 2305 |
| `SOUND_Swap_sound_effects` | Swap two sound effects (for sorting). | 2461 |
| `SOUND_Compare_sound_effects` | Compare two sound effects (for sorting). | 2497 |
| `SOUND_Update_located_sound_effects` | Determine if any located sound effects should be started. | 2537 |
| `SOUND_Start_sound_effect` | Start playing a sound effect. | 2665 |
| `SOUND_Update_sound_effect` | Update a playing sound effect. | 2784 |
| `SOUND_Stop_sound_effect` | SOUND_Stop playing a sound effect. | 2848 |
| `SOUND_Delete_sound_effect` | Delete a sound effect. | 2897 |
| `SOUND_Stop_all_digital_channels` | Stop all digital channels that are currently playing. | 2936 |
| `SOUND_Stop_digital_channel` | Stop playing a digital channel. | 2969 |

### SPELLS.C

`src/ALBION/SRC/SPELLS.C` – Zauber außerhalb des Kampfes (Heilen, Zustände heilen, Licht, Karte …).

| Funktion | Zweck | Zeile |
|---|---|---|
| `C0_Spell_9_handler` | Spell handler. | 92 |
| `Do_C0_Spell_9` | Class 0 spell 9: heal a party member (life points). **R** | 121 |
| `C0_Spell_17_handler` | Spell handler. | 155 |
| `Do_C0_Spell_17` | Class 0 spell 17: cure the condition STONED. **R** | 184 |
| `C0_Spell_18_handler` | Spell handler. | 209 |
| `Do_C0_Spell_18` | Class 0 spell 18: cure the condition BLIND. **R** | 238 |
| `C0_Spell_19_handler` | Spell handler. | 263 |
| `Do_C0_Spell_19` | Class 0 spell 19: cure the condition POISONED. **R** | 292 |
| `C0_Spell_21_handler` | Spell handler. | 317 |
| `C1_Spell_1_handler` | Spell handler. | 352 |
| `Do_C1_Spell_1` | Class 1 spell 1: cure all conditions and heal a party member. **R** | 381 |
| `C1_Spell_2_handler` | Spell handler. | 426 |
| `C1_Spell_3_handler` | Spell handler. | 471 |
| `C1_Spell_5_handler` | Spell handler. | 506 |
| `Do_C1_Spell_5` | Class 1 spell 5: heal a party member (life points). **R** | 535 |
| `C1_Spell_11_handler` | Spell handler. | 569 |
| `Do_C1_Spell_11` | Class 1 spell 11: remove exhaustion and let a party member recuperate. **R** | 611 |
| `C2_Spell_7_handler` | Spell handler. | 639 |
| `Do_C2_Spell_7` | Class 2 spell 7: heal a party member (life points). **R** | 668 |

### STATAREA.C

`src/ALBION/SRC/STATAREA.C` – Statusbereich: Gruppenporträts, Lebens- und Magiepunkte, Zustandsanzeigen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Init_status_area` | Initialize the status area. | 283 |
| `Init_Status_area_object` | Initialize method of Status_area object. | 331 |
| `Draw_Status_area_object` | Draw method of Status area object. | 380 |
| `Update_Status_area` | Update the Status area object. | 419 |
| `Init_party_display` | Initialize the party display. | 457 |
| `Reset_party_display` | Reset the party display. | 493 |
| `Init_Party_display_object` | Initialize method of Party display object. | 525 |
| `Draw_Party_display_object` | Draw method of Party display object. | 585 |
| `Update_Party_display_object` | Update method of Party display object. | 617 |
| `Init_Party_member_object` | Initialize method of Party member object. | 663 |
| `Draw_Party_member_object` | Draw method of Party member object. | 708 |
| `Update_Party_member_object` | Update method of Party member object. | 758 |
| `Highlight_Party_member_object` | Highlight method of Party member object. | 847 |
| `Feedback_Party_member_object` | Feedback method of Party member object. | 901 |
| `Left_Party_member_object` | Left method of Party member object. | 951 |
| `DLeft_Party_member_object` | DLeft method of Party member object. | 987 |
| `Pop_up_Party_member_object` | Pop-up method of Party member object. | 1026 |
| `Help_Party_member_object` | Help method of Party member object. | 1074 |
| `Touch_Party_member_object` | Touch method of Party member object. | 1210 |
| `Drop_Party_member_object` | Drop method of Party member object. | 1251 |
| `Inquire_drop_Party_member_object` | Inquire drop method of Party member object. | 1425 |
| `Calculate_bar_sizes` | Calculate LP & SP bar sizes. | 1498 |
| `Draw_party_members` | Draw all party members in the status area. | 1572 |
| `Highlight_party_members` | Draw all party members in the status area, highlighting one. | 1646 |
| `Feedback_party_members` | Draw all party members in the status area, "feedbacking" one. | 1761 |
| `Display_party_member_portrait` | Display a party member's portrait. | 1878 |
| `Display_party_status_bars` | Draw all party members' status bars in the status area. | 1956 |
| `Display_party_damage` | Draw all party members' damage displays in the status area. | 2129 |
| `Party_member_PUM_evaluator` | Evaluate party member pop-up menu. | 2228 |
| `PUM_Go_inventory` | Go to inventory mode 1 (party member pop-up menu). | 2340 |
| `PUM_Use_magic` | Use magic (party member pop-up menu). | 2364 |
| `PUM_Make_active_member` | Make someone the active member (party member pop-up menu). | 2388 |
| `PUM_Talk_to_member` | Talk to a party member (party member pop-up menu). | 2412 |
| `PUM_Toggle_member` | Toggle a party member (party member pop-up menu). | 2459 |
| `Draw_Help_line_object` | Draw method of Help_line object. | 2500 |
| `Update_Help_line_object` | Update method of Help_line object. | 2588 |
| `Set_Help_line_object` | Set method of Help_line object. | 2633 |
| `Update_help_line` | Update the Help_line object. | 2692 |
| `Init_Permanent_text_object` | Init method of Permanent_text object. | 2727 |
| `Draw_Permanent_text_object` | Draw method of Permanent_text object. | 2764 |
| `Update_Permanent_text_object` | Update method of Permanent_text object. | 2840 |
| `Set_Permanent_text_object` | Set method of Permanent_text object. | 2896 |
| `Set_permanent_message_nr` | Set a new permanent message number. | 2983 |
| `Set_permanent_text` | Set a new permanent text. | 3017 |
| `Clear_permanent_text` | Clear the permanent text. | 3051 |

### VERSION.C

`src/ALBION/SRC/VERSION.C` – Versionsnummer und -text des Spiels.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Get_version_string` | Get Albion version as a string. | 51 |
| `Get_version_number` | Get Albion version as a number. | 86 |

### XFTYPES.C

`src/ALBION/SRC/XFTYPES.C` – Dateiarten und Datenpfade: welche XLD-Datei wo liegt, CD-Pfad, sprachabhängige Dateien.

| Funktion | Zweck | Zeile |
|---|---|---|
| `Check_FLIC` | Initialize data paths. | 880 |
| `Init_data_paths` | Build the list of data paths (current directory and the path of ALBION.EXE). **R** | 940 |
| `Add_data_path` | Add a new data path. | 992 |
| `Select_data_path` | Select a data path. | 1025 |
| `Search_second_data_path` | Look for a second data path. | 1055 |
| `Check_CD` | Check if the second data path is the Albion CD. | 1126 |
| `Prepare_file_type` | Prepare an entry from the eXtended file type array. | 1178 |
| `Load_file` | Load a file. | 1259 |
| `Save_file` | Save a file. | 1338 |
| `Get_subfile_length` | Get the length of a subfile from a library. | 1372 |
| `Open_subfile` | Open a subfile from a library. | 1453 |
| `Close_subfile` | Close a subfile from a library. | 1540 |
| `Load_subfile` | Load a subfile from a library. | 1567 |
| `Save_subfile` | Save a subfile into a library. | 1647 |
| `Load_unique_subfile` | Load a unique subfile from a library. | 1724 |
| `Load_full_batch` | Load a batch of subfiles from a library. ALL files in the batch must be loaded. | 1810 |
| `Load_partial_batch` | Load a batch of subfiles from a library. NOT all files in the batch must be loaded. | 1903 |
| `Read_INI_variable` | Read a variable from the INI file. | 1992 |
| `Write_INI_variable` | Write a variable in the INI file. | 2203 |

## Blue-Byte-Bibliothek PCLIB32

### BBBASMEM.C

`src/PCLIB32/SRC/BBBASMEM/BBBASMEM.C` – Grundspeicher: Blöcke vom DOS-Extender holen und freigeben.

| Funktion | Zweck | Zeile |
|---|---|---|
| `BASEMEM_Init` | Initialize base memory. | 180 |
| `BASEMEM_Exit` | Exit base memory. | 257 |
| `BASEMEM_Get_largest_block` | Return the size of the largest, possibly virtual, free block of memory. | 301 |
| `BASEMEM_Get_largest_real_block` | Return the size of the largest NON-VIRTUAL free block of memory. | 383 |
| `BASEMEM_Get_free_memory` | Return the total amount of free memory. | 480 |
| `BASEMEM_Alloc` | Allocate a block of memory. | 582 |
| `BASEMEM_Free` | Free an allocated memory block. | 888 |
| `BASEMEM_Resize` | Resize a block of memory. | 1044 |
| `BASEMEM_Lock_region` | Lock a region of memory. | 1337 |
| `BASEMEM_Unlock_region` | Unlock a region of memory. | 1401 |
| `BASEMEM_FillMemByte` | Fills a buffer with a byte value. | 1466 |
| `BASEMEM_FillMemLong` | Fills a buffer with a longword value. | 1510 |
| `BASEMEM_CopyMem` | Copy one buffer into an other. | 1560 |
| `BASEMEM_CopyBlock` | Copy block into an other. | 1612 |
| `BASEMEM_Align` | Align the size or address of a memory block. | 1644 |
| `BASEMEM_Report_error` | Report a BASEMEM error. | 1673 |
| `BASEMEM_Print_error` | Print a BASEMEM error. | 1717 |
| `BASEMEM_Report` | Print a memory report. | 1798 |

### BBDOS.C

`src/PCLIB32/SRC/BBDOS/BBDOS.C` – Dateizugriff über DOS: öffnen, lesen, schreiben, suchen, Verzeichnisse.

| Funktion | Zweck | Zeile |
|---|---|---|
| `DOS_Init` | Initialize DOS library and structures. | 98 |
| `DOS_Exit` | Exit DOS library. | 179 |
| `DOS_Open` | Open a file. | 245 |
| `DOS_Close` | Close file | 387 |
| `DOS_Read` | Read a given number of bytes from an opened file. | 456 |
| `DOS_Write` | Write a given number of bytes to an opened file. | 552 |
| `DOS_Seek` | Set offset to a given position | 649 |
| `DOS_ReadFile` | Read a complete file. | 744 |
| `DOS_WriteFile` | Write a buffer as a file to disk. | 922 |
| `DOS_Delete` | Deletes a file. | 1016 |
| `DOS_GetFileLength` | Get the length of a file in bytes. | 1047 |
| `DOS_Exist` | Funktion stellt fest ob File existiert | 1144 |
| `DOS_GetCurrentDir` | Return the current drive and directory. | 1221 |
| `DOS_SetCurrentDir` | Change the current drive and directory. | 1284 |
| `DOS_Eof` | Testet ob Filezeiger sich am Ende Des Files befindet | 1351 |
| `DOS_GetSeekPosition` | Get the seek position of a file. | 1433 |

### BBDSA.C

`src/PCLIB32/SRC/BBDSA/BBDSA.C` – Bildschirm (DSA): Grafikmodi (VGA, Chain-4, VESA), Bildschirm öffnen, Doppelpuffer, Palette.

| Funktion | Zweck | Zeile |
|---|---|---|
| `DSA_Init` | Initialisiert SCREENPORT strukture. | 112 |
| `DSA_Exit` | Exit the DSA screen library (closes a screen that is still open). | 171 |
| `DSA_OpenScr` | Open a screen for an OPM (VGA, chain-4 or VESA mode). **R** | 251 |
| `DSA_CloseScr` | Close a screen (GUI: window ). Frees all memory allocated by DSA_OpenScreen(). Schaltet Mauszeiger aus | 675 |
| `DSA_DoubleBuffer` | schaltet Bildschirme um wenn das entsprechende Bit im System_ActiveScreenport gesetzt ist | 735 |
| `DSA_WaitTOF` | wartet auf Bildschirm Anfang bzw Ende des VBLS | 808 |
| `DSA_WaitBOF` | wartet auf Bildschirm Ende bzw Anfang des VBLS | 835 |
| `DSA_CopyMainOPMToScr` | Kopiert MainOPM auf den Bildschirm. je nachdem ob als copyflag DSA_Always oder DSA_Changed übergeben wird, wird nur kopiert falls das OPM verändert wurde | 864 |
| `DSA_CopyOPMToScr` | Kopiert OPM auf den Bildschirm. je nachdem ob als copyflag DSA_Always oder DSA_Changed übergeben wird, wird nur kopiert falls das OPM verändert wurde | 999 |
| `DSA_CopyScrToOPM` | Kopiert Ausschnitt des Bildschirms in OPM Breite und Höhe wird aus OPM entnommen. | 1202 |
| `DSA_SPal` | Kopiert einen Ausschnitt aus einer Palette in die ScreenportPalette | 1343 |
| `DSA_APal` | Activiert die aktuelle ScreenPalette | 1410 |
| `DSA_SCol` | Setzt eine Farbe in der ScreenportPalette | 1440 |

### BBERROR.C

`src/PCLIB32/SRC/BBERROR/BBERROR.C` – Fehlerstapel der Bibliothek: Fehler ablegen, holen, ausgeben.

| Funktion | Zweck | Zeile |
|---|---|---|
| `ERROR_Init` | Initialize error library. | 81 |
| `ERROR_ClearStack` | Clear error stack (set number of error messages to 0). | 118 |
| `ERROR_SetOutputFuncPtr` | Set pointer to string output function. | 150 |
| `ERROR_PushError` | Pushes one error message onto the stack | 187 |
| `ERROR_PopError` | Pops one error message from the stack. | 281 |
| `ERROR_StackEmpty` | Checks if the error stack is empty. | 311 |
| `ERROR_PrintAllErrors` | Call print function for all errors on error stack. | 349 |
| `BBERROR_LocalPrintError` | Format an internal error of the error library ("INTERNAL ERROR: ..."). | 475 |

### BBEVENT.C

`src/PCLIB32/SRC/BBEVENT/BBEVENT.C` – Ereignispuffer für Maus und Tastatur, Tastaturabfrage über das BIOS.

| Funktion | Zweck | Zeile |
|---|---|---|
| `BLEV_Init` | Initialize the event library (event buffer, mouse and keyboard). | 69 |
| `BLEV_Exit` | Exit the event library. | 130 |
| `BLEV_IsEventWaiting` | Warten bis Event auftritt | 164 |
| `BLEV_ClearAllEvents` | Event Stack entleeren | 190 |
| `BLEV_PutEvent` | Event auf Eventstack kopieren | 222 |
| `BLEV_GetEvent` | Event vom EventStack holen | 277 |
| `BLEV_GetMousePos` | Mausposition X auslesen | 336 |
| `BLEV_Check_keyboard` | Read pending keys through the BIOS and turn them into events. **R** | 389 |
| `BLEV_Init_keyboard` | Fill the scan code table for the BIOS keyboard. **R** | 457 |

### BBLBM.C

`src/PCLIB32/SRC/BBLBM/BBLBM.C` – LBM-Bilder (Deluxe Paint) laden und anzeigen.

| Funktion | Zweck | Zeile |
|---|---|---|
| `LBM_FindChunk` | Search a chunk in an LBM file in memory. **R** | 73 |
| `LBM_GetPal` | Copy the colour palette (CMAP chunk) of an LBM file into a palette. **R** | 146 |
| `LBM_DisplayLBMinOPM` | Unpack the picture of an LBM file into an OPM (packed or unpacked body). **R** | 225 |
| `LBM_DisplayLBM` | Loads and displays a LBM. | 400 |
| `LBM_DisplayTGA` | None. | 514 |

### BBTGA.C

`src/PCLIB32/SRC/BBLBM/BBTGA.C` – TGA-Bilder (Targa) laden und speichern.

| Funktion | Zweck | Zeile |
|---|---|---|
| `TGA_SetPixel` | Set a pixel in a high-colour or true-colour OPM. **R** | 90 |
| `TGA_GetPixel` | Get the colour of a pixel in a high-colour or true-colour OPM. **R** | 155 |
| `convert_targa_color` | Convert a Targa pixel (2, 3 or 4 bytes) into a colour. **R** | 219 |
| `tga_read` | Read bytes of a Targa file, either from memory or buffered from a file. **R** | 284 |
| `LBM_ReadTGA` | TGA Bild laden in ein OPM mit 2,3,4 Byte Pro Pixel | 375 |
| `LBM_WriteTGA` | Save an OPM as an uncompressed Targa (TGA) file. | 599 |

### BBMEM.C

`src/PCLIB32/SRC/BBMEM/BBMEM.C` – Speicherverwaltung mit Handles: Arbeitsbereiche, Blöcke, Zeiger anfordern und freigeben.

| Funktion | Zweck | Zeile |
|---|---|---|
| `MEM_Init_memory` | Initializes the memory manager and the first workspace. | 61 |
| `MEM_Exit_memory` | Exits the memory manager. All memory is returned to the OS. | 261 |
| `MEM_Get_total_memory` | Get the total amount of memory of a certain type. | 303 |
| `MEM_Reset_memory` | Resets the memory manager. All memory workspaces apart from the first one and all handles will be destroyed. All areas will be initialized. | 347 |
| `MEM_Init_workspace` | Initializes a memory workspace. All memory areas belonging to this workspace are initialized. | 390 |
| `MEM_Reset_workspace` | Resets a memory workspace. All memory areas belonging to this workspace are initialized. | 426 |
| `MEM_Init_area` | Initializes a memory area. All memory entries linked to this one and their handles are deleted. One big, free memory entry is created. | 458 |
| `MEM_Report_error` | Report a memory manager error. | 520 |
| `MEM_Report_critical_error` | Report a critical memory manager error. | 560 |
| `MEM_Print_error` | Print a memory manager error. | 594 |
| `MEM_Find_free_entry` | Find a free memory entry. | 670 |
| `MEM_Add_entry` | Insert a memory entry in the memory lists. | 765 |
| `MEM_Delete_entry` | Delete a memory entry from the memory lists. | 812 |
| `MEM_Clear_all_handles` | Clear all memory handles. | 859 |
| `MEM_Clear_all_claims` | Clear all memory claims in the current workspace. *(aus)* | 903 |
| `MEM_Check_if_handle_is_legal` | Check if a memory handle is legal. | 961 |
| `MEM_Get_pointer` | Get an UNCLAIMED pointer to a memory block. | 1003 |
| `MEM_Claim_pointer` | Claim a memory block. | 1056 |
| `MEM_Free_pointer` | Free a pointer to a memory block. | 1128 |
| `MEM_Create_memory_handle` | Create a new memory handle. | 1190 |
| `MEM_Destroy_memory_handle` | Destroy a memory handle. | 1275 |
| `MEM_Get_block_size` | Get the size of a memory block. | 1317 |
| `MEM_Get_file_index` | Get the file index of a memory handle. | 1362 |
| `MEM_Resize_memory` | Change the size of a memory block. | 1404 |
| `MEM_Free_memory` | Free a memory block. | 1513 |
| `MEM_Kill_memory` | Kill a memory block. | 1591 |
| `MEM_Invalidate_memory` | Invalidate a memory block. | 1649 |
| `MEM_Clear_memory` | Clear a memory block. | 1686 |
| `MEM_Relocate` | Copy a memory block from one location to another. | 1735 |
| `MEM_Add_workspace` | Initializes a workspace and returns the workspace number. *(aus)* | 1786 |
| `MEM_Delete_workspace` | Terminates a workspace. *(aus)* | 1892 |
| `MEM_Push_workspace` | Pushes a new workspace on the workspace stack. *(aus)* | 1952 |
| `MEM_Pop_workspace` | Pops a workspace from the top of the workspace stack. *(aus)* | 1993 |
| `MEM_Change_workspace` | Change the workspace on the top of the workspace stack. *(aus)* | 2027 |
| `MEM_Init_memory` | Initializes the memory manager and the first workspace. *(aus)* | 2061 |

### BBMEMALO.C

`src/PCLIB32/SRC/BBMEM/BBMEMALO.C` – Speicherverwaltung: Blöcke belegen, verschieben, Müll sammeln.

| Funktion | Zweck | Zeile |
|---|---|---|
| `MEM_Start_lengthy_operation` | Indicate the start of a lengthy operation. | 73 |
| `MEM_End_lengthy_operation` | Indicate the end of a lengthy operation. | 105 |
| `MEM_Inquire_memory` | Inquire if a certain memory block could be allocated. | 147 |
| `MEM_Allocate_memory` | Allocate a block of free memory in the current workspace. | 206 |
| `MEM_Do_allocate` | Allocate a memory block in the current workspace. | 233 |
| `MEM_Armageddon` | Drown EVERYTHING & collect garbage in the current workspace. | 337 |
| `MEM_Allocate_block` | Allocate a memory block. | 378 |
| `MEM_Collect_garbage` | Collect garbage in a memory area. | 430 |
| `MEM_Relocate_memory_block` | Relocate a memory block. | 501 |
| `MEM_Find_LFB_in_garbage` | Find the Largest Free Block in the part of a memory area where garbage has already been collected. | 631 |
| `MEM_Move_memory_block` | Move a memory block. | 696 |
| `MEM_Find_LFB` | Find the Largest Free Block in a memory area. | 754 |
| `MEM_Calculate_TFM` | Calculate the Total Free Memory in a memory area. | 802 |
| `MEM_Calculate_EMG` | Calculate the Extra Memory Gained in a memory area. | 846 |
| `MEM_Drown_memory` | "Drown" all memory blocks in a memory area which aren't allocated and which have a priority below sea level. | 903 |
| `MEM_Merge_memory_block` | Try to merge memory block with previous and/or next entry. | 963 |
| `MEM_Split_memory_block` | Split a memory block in two parts. | 1044 |
| `MEM_Validate_handles` | Validate all memory handles in the current workspace. | 1101 |
| `MEM_Kill_unclaimed_memory` | Kill all unclaimed memory blocks in the current workspace. | 1163 |
| `MEM_Alloc_pass_standard` | Standard memory allocation pass. | 1225 |
| `MEM_Alloc_pass_garbage` | Garbage collecting memory allocation pass. | 1293 |
| `MEM_Alloc_pass_drown` | Memory drowning allocation pass. | 1367 |
| `MEM_Alloc_pass_juggle` | Memory juggling allocation pass. *(aus)* | 1465 |
| `MEM_Alloc_pass_clean` | Memory cleaning allocation pass. | 1577 |
| `MEM_Reallocate_memory` | Find and re-allocate a persistent memory block. | 1621 |
| `MEM_Duplicate_memory` | Find and make a unique copy of a persistent memory block. | 1676 |
| `MEM_Search_persistent_block` | Search a certain valid persistent memory block. | 1746 |
| `MEM_Do_reallocate` | Actually re-allocate a memory block. | 1803 |
| `MEM_Find_memory_area` | Find the memory area belonging to a memory block. | 1895 |
| `MEM_Find_memory_workspace` | Find the memory workspace belonging to a memory area. | 1932 |

### BBMEMCHK.C

`src/PCLIB32/SRC/BBMEM/BBMEMCHK.C` – Speicherverwaltung: Prüfung der inneren Stimmigkeit, Übersicht.

| Funktion | Zweck | Zeile |
|---|---|---|
| `MEM_Check_memory` | Check the internal consistency of the memory manager. | 52 |
| `MEM_Check_workspace` | Check the internal consistency of a memory workspace . | 93 |
| `MEM_Check_area` | Check the internal consistency of a memory area. | 129 |
| `MEM_List` | List the current status of the memory manager. *(aus)* | 297 |

### BBMEMVAR.C

`src/PCLIB32/SRC/BBMEM/BBMEMVAR.C` – Variablen der Speicherverwaltung.

Keine Funktionen (nur Daten).

### BBMTH.C

`src/PCLIB32/SRC/BBMTH/BBMTH.C` – Mathematik: Wurzel, Zufall, Sinus, Kosinus, Arkustangens, Vektorlänge.

| Funktion | Zweck | Zeile |
|---|---|---|
| `MTH_sqrt` | Square root (of the absolute value; negative values are reported as error). | 60 |
| `MTH_initrnd` | Initialize the random number generator. | 95 |
| `MTH_rnd` | Return a random number. | 122 |
| `MTH_veklen` | Länge des übergebenen Vektors ausrechnen | 150 |
| `MTH_sin` | Sine from the lookup table (angle 0...65535 = 0...360 degrees). | 177 |
| `MTH_cos` | Cosine from the lookup table (angle 0...65535 = 0...360 degrees). | 216 |
| `MTH_atan` | Arc tangent of the vector (x, y) as angle. | 261 |

### SINTAB.C

`src/PCLIB32/SRC/BBMTH/SINTAB.C` – Sinustabelle.

Keine Funktionen (nur Daten).

### TANTAB.C

`src/PCLIB32/SRC/BBMTH/TANTAB.C` – Tangenstabelle.

Keine Funktionen (nur Daten).

### BBOPM.C

`src/PCLIB32/SRC/BBOPM/BBOPM.C` – OPMs (Offscreen Pixel Maps): Bildpuffer anlegen, Pixel, Linien, Kästen, Kopieren.

| Funktion | Zweck | Zeile |
|---|---|---|
| `OPM_New` | Initialize a OPM structure. All fields of the OPM structure are initialized. Global OPM offset is set to (0\|0). Clipping retangle is set to (0\|0)-(width\|height). | 76 |
| `OPM_Del` | Free a OPM structure. Free memory of OPM if it was allocated by OPM_New(). Invalid status flag set. | 204 |
| `OPM_SetVirtualPosition` | Set the position of a virtual OPM. Routine verändert die Quellkopierposition -> opm.data, d.h. das OPM erscheint auf dem Bildschirm weiterhin an der gleichen Stelle nur mit dem Unterschied das von einem anderen Datenbereich kopiert wird. (Nützlich für Scrollroutinen) | 256 |
| `OPM_CreateVirtualOPM` | Initialize a virtual OPM. A virtual OPM has no own pixel map. It works on a part of a pixel map of a given OPM. Sollte der Quellopmbereich durch das virtuelle OPM überschritten werden so werden die Clippinggrenzen entsprechend gesetzt und xoffset,yoffset wird verwendet um später die richtige Position zu erreichen * Diese Funktion kann auch verwendet werden um eine neue Position oder Grösse für das virtuelle OPM anzugeben, es wird kein Speicher angefordert oder freigegeben. | 346 |
| `OPM_SetPixel` | Set a pixel in an OPM object. The OPM offset is used and the clip area is checked. If the pixel is set OPMSTAT_CHANGED is set in the OPM status flag set. | 462 |
| `OPM_GetPixel` | Get the color of a pixel on a given position in a given OPM. | 511 |
| `OPM_HorLine` | Draw a horizontal line into an OPM object. If a pixel is set OPMSTAT_CHANGED is set in the OPM status flag set. | 557 |
| `OPM_VerLine` | Draw a vertical line into an OPM object. If a pixel is set OPMSTAT_CHANGED is set in the OPM status flag set. | 623 |
| `OPM_Box` | Draw a box into an OPM. If a pixel is set OPMSTAT_CHANGED is set in the OPM status flag set. | 688 |
| `OPM_FillBox` | Draw a filled box into an OPM. If a pixel is set OPMSTAT_CHANGED is set in the OPM status flag set. | 783 |
| `OPM_CopyGFXOPM` | Copy a GTO into a OPM. If a pixel is set OPMSTAT_CHANGED is set in the OPM status flag set. | 866 |
| `OPM_CopyOPMOPM` | Copy a retangle from a source OPM into a destination OPM. If a pixel is set OPMSTAT_CHANGED is set in the destination OPM status flag set. Es wird sowohl das Source Opm als auch das ZielOpm geclippt | 1032 |
| `OPM_Write` | Gibt einen Text mit internem Zeichensatz aus | 1245 |
| `OPM_printf` | Ähnliche Funktionsweise wie printf nur mit OPMS | 1280 |
| `OPM_ChangeColor` | Jede Farbe eines OPMS anhand einer 256 Byte grossen IndexTabelle innerhalb des Clipfensters ändern. | 1325 |
| `OPM_Zoom` | Zoomt ein Opm in ein beliebieges anderes Opm | 1370 |

### BBSYSTEM.C

`src/PCLIB32/SRC/BBSYSTEM/BBSYSTEM.C` – Systemanbindung: Zeitgeber-Interrupt, Maustreiber, Mauszeiger, Tastaturinterrupt, Start und Ende.

| Funktion | Zweck | Zeile |
|---|---|---|
| `SYSTEM_Int09` | Keyboard interrupt: register key presses and releases. **R** | 164 |
| `SYSTEM_Int08` | Timer interrupt, runs the system timer and chains to the old handler. **R** | 209 |
| `SYSTEM_Timer_function` | System timer tick (ticks, double click timeout). **R** | 253 |
| `Mouse_handler` | Mouse driver callback, turns mouse actions into events. **R** | 322 |
| `cbc_end` | Empty function that marks the end of the locked interrupt code. **R** | 546 |
| `lock_region` | if(cbd.mcode&2){ /* linke Taste gedrückt */ cbd.lastlclick=ticks; } if(cbd.mcode&8){ /* rechte Taste gedrückt */ cbd.lastrclick=ticks; } *(aus)* | 567 |
| `SYSTEM_Init` | Init operating system and internal variables Mausclipping wird standartmäßif auf 0,0,639,479 gesetzt bis OpenScreen ausgeführt wird | 635 |
| `SYSTEM_Exit` | Exit GUI and reinit operating system. | 894 |
| `SYSTEM_SystemTask` | Let the operating system some time to work. | 1012 |
| `SYSTEM_SystemAlert` | Show a dialog box. | 1184 |
| `SYSTEM_GetBLEVStatusLong` | Generate status for BBEVENT messages (-> BBEVENT.h). | 1222 |
| `SYSTEM_MouseRestore` | Restore the background under the mouse pointer. **R** | 1294 |
| `SYSTEM_MouseDisplay` | Save the background and draw the mouse pointer. **R** | 1420 |
| `SYSTEM_ShowMousePtr` | Schaltet Mauszeiger ein und updatet in unabhängig von den OPMToScreen Routinen im Interrupt | 1557 |
| `SYSTEM_HideMousePtr` | Schaltet Mauszeiger aus | 1760 |
| `SYSTEM_GetTicks` | SYSTEM_GetTicks | 1805 |
| `SYSTEM_WaitTicks` | SYSTEM_WaitTicks( UNLONG waitticks ) | 1830 |
| `SYSTEM_SetMouseArea` | Set the mouse clip area. | 1867 |
| `SYSTEM_SetMousePtr` | Set the position of the mouse pointer. | 1920 |
| `SYS_PrintError` | Format a system library error message into a string buffer. **R** | 1959 |

### KEYINTRN.C

`src/PCLIB32/SRC/BBSYSTEM/KEYINTRN.C` – Tabellen für die Tastatur.

Keine Funktionen (nur Daten).

### STDMOUSP.C

`src/PCLIB32/SRC/BBSYSTEM/STDMOUSP.C` – Standard-Mauszeiger.

Keine Funktionen (nur Daten).

## Setup-Programm (nicht Teil von MAIN.EXE)

### BASEIO.C

`src/ALBION/OUTSIDE/BBSETUP/SRC/BASEIO.C` – Installations- und Einrichtungsprogramm (Laufwerk wählen, Dateien kopieren, Soundkarte und Grafikmodus einstellen, INI schreiben).

| Funktion | Zweck | Zeile |
|---|---|---|
| `IsDriveReal` | Ist Laufwerk physikalisch vorhanden oder nur ASSIGNed ? Int 21h, AH=44h, AL=0Eh - Drive=1=A:> | 14 |
| `IfExists` | Gibt wahr zurück falls das File oder die Directory existiert | 28 |
| `IfExistsFile` | Gibt wahr zurück falls das File existiert | 42 |
| `IfExistsDir` | Gibt wahr zurück falls das Verzeichnis existiert | 61 |
| `CreateFile` | Legt 'ne leere Datei an. Weiß nicht wozu, aber er kann es: | 83 |
| `IfWindows` | Gibt TRUE zurück, falls Setup in einer Windows-DosBox läuft *(aus)* | 102 |
| `GetLastdrive` | Dummy-Funktion die später mal den Wert des "Lastdrive"-Settings liefern soll! | 138 |

### BASEWIN.C

`src/ALBION/OUTSIDE/BBSETUP/SRC/BASEWIN.C` – Installations- und Einrichtungsprogramm (Laufwerk wählen, Dateien kopieren, Soundkarte und Grafikmodus einstellen, INI schreiben).

| Funktion | Zweck | Zeile |
|---|---|---|
| `DrawArrow` | Zeichnet einen Pfeil an (x\|y) mit Richtung oben oder unten | 9 |
| `Rectangle` | Ein ungefülltes Rechteck zeichnen: | 25 |
| `Rectangle3d` | Ein gefülltes Rechteck mit den 3d-ecken (Hell/Dunkel) zeichnen: | 38 |
| `Window3d` | Ein Fenster mit den 3d-ecken (Hell/Dunkel) zeichnen: | 63 |
| `DrawButton` | Zeichnet einen Standart-Button mit diesem Schatten-Rahmen | 86 |
| `DrawWinShadow` | Zeichnet hinter das anzgegebene Fenster einen Schatten: | 108 |
| `PushButton` | Drückt einen Knopf rein: | 127 |
| `UnPushButton` | Ziegt einen Knopf wieder raus: | 146 |
| `RefreshFixedPalette` | Refresht den fixen Teil der Palette (Die Systemfarben) | 171 |
| `PrintTextInFrame` | versucht einen Text in einen Rahmen zu drucken. TRUE wenn er reinpasst. | 221 |
| `PrintCenteredTextInFrame` | versucht eine Textzeile zentriert in einen Rahmen zu drucken. rc siehe oben. | 326 |
| `PixelStringLength` | Berechnet die Stringlänge in Pixeln eines Strings: | 340 |
| `PixelCharLength` | Berechnet die Stringlönge in Pixeln eines Zeichens: | 359 |
| `ScaleCopyOpm` | Kopiert Source in Target auf je volle Größe | 371 |

### BROWSER.C

`src/ALBION/OUTSIDE/BBSETUP/SRC/BROWSER.C` – Installations- und Einrichtungsprogramm (Laufwerk wählen, Dateien kopieren, Soundkarte und Grafikmodus einstellen, INI schreiben).

| Funktion | Zweck | Zeile |
|---|---|---|
| `BrowseFile` | Hauptfunktion, die von außen einfach aufgerufen wird um ein File zu zeigen: | 9 |
| `LoadBrowseFile` | Läd ein Textfile ohne Änderungen in eine SCRIPT-Struktur: | 278 |

### DEBUG.C

`src/ALBION/OUTSIDE/BBSETUP/SRC/DEBUG.C` – Installations- und Einrichtungsprogramm (Laufwerk wählen, Dateien kopieren, Soundkarte und Grafikmodus einstellen, INI schreiben).

| Funktion | Zweck | Zeile |
|---|---|---|
| `InternalError` | Programm verlassen und Meldung ausgeben oder nur Meldung ausgeben: Changed ErrNum from SISHORT to int - JH | 11 |
| `DoDebugBreak` | Im Debugger einen automatischen Breakpoint setzen: | 70 |
| `THMalloc` | Sorry Jurie, aber alles was ich brauche ist eine sichere Methode um Speicherplatz zu bekommen. Wenn keiner da ist, dann läuft das Programm nicht, so einfach ist das. Daher hier eine start abgespeckte Routine aus meinem eigenen Memory-Management System: | 84 |

### EVENT.C

`src/ALBION/OUTSIDE/BBSETUP/SRC/EVENT.C` – Installations- und Einrichtungsprogramm (Laufwerk wählen, Dateien kopieren, Soundkarte und Grafikmodus einstellen, INI schreiben).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Get_event` | NAME      : Get_event FUNCTION  : Get an input event and handle input recording / playback. FILE      : CONTROL.C AUTHOR    : Jurie Horneman FIRST     : 19.09.94 12:24 LAST      : 19.09.94 12:24 INPUTS    : struct BLEV_Event_struct *Event - Event. RESULT    : None. BUGS      : No known. SEE ALSO  : | 26 |
| `Update_input` | NAME      : Update_input FUNCTION  : Update input. FILE      : CONTROL.C AUTHOR    : Jurie Horneman FIRST     : 05.09.94 13:32 LAST      : 05.09.94 13:32 INPUTS    : None. RESULT    : None. BUGS      : No known. NOTES     : - This function makes sure that the events will be read and that the current mouse coordinates and button state remain up to date. SEE ALSO  : | 101 |

### GLOBAL.C

`src/ALBION/OUTSIDE/BBSETUP/SRC/GLOBAL.C` – Installations- und Einrichtungsprogramm (Laufwerk wählen, Dateien kopieren, Soundkarte und Grafikmodus einstellen, INI schreiben).

Keine Funktionen (nur Daten).

### INI.C

`src/ALBION/OUTSIDE/BBSETUP/SRC/INI.C` – Installations- und Einrichtungsprogramm (Laufwerk wählen, Dateien kopieren, Soundkarte und Grafikmodus einstellen, INI schreiben).

| Funktion | Zweck | Zeile |
|---|---|---|
| `IniRead` | static UNCHAR IniFilename[] = "SETUP.INI"; | 17 |
| `IniSet` | static UNCHAR IniFilename[] = "SETUP.INI"; | 37 |
| `BrutalIniSet` | static UNCHAR IniFilename[] = "SETUP.INI"; | 48 |
| `StrRemoveEndingCodes` | entfernt alle CodeString-Zeichen die am Ende des Strings vorkommen: *(aus)* | 68 |
| `IniSet` | Ändert eine Variable in "Filename" (bzw. fügt sie ggf. hinzu) *(aus)* | 88 |
| `BrutalIniSet` | Fügt eine Variable in "Filename" ohne Rücksicht hinzu: *(aus)* | 216 |
| `IniDelete` | Löscht ein Variable aus "Filename" (Sections werden nicht gelöscht) *(aus)* | 312 |
| `IniRead` | Gibt einen Pointer auf einen static-buffer mit dem Eintrag zurück (oder NULL) *(aus)* | 406 |
| `UpdateIni` | Aktualisiert alle Daten in der INI-Datei: | 461 |
| `LoadIni` | Probiert die Ini zu laden: | 506 |
| `BenchPixelSpeed` | Probiert wieviele Pixel man pro sec in die Grafikkarte schieben kann: *(aus)* | 521 |
| `CalculateIniFilename` | Den Ini-Pfad ableiten: | 546 |
| `Read_INI_variable` | Read a variable from the INI file. | 597 |
| `Write_INI_variable` | Write a variable in the INI file. | 756 |

### IO.C

`src/ALBION/OUTSIDE/BBSETUP/SRC/IO.C` – Installations- und Einrichtungsprogramm (Laufwerk wählen, Dateien kopieren, Soundkarte und Grafikmodus einstellen, INI schreiben).

| Funktion | Zweck | Zeile |
|---|---|---|
| `ChangeDirAndDriveTo` | Wechselt Laufwerk und Pfad (Files dürfen nicht mit angegeben werden !) | 9 |
| `CopyOneFile` | Kopiert ein File von Source nach Ziel (Beidesmale Filenamen mitangeben) (das r/o flag wird dabei nicht mitkopiert) | 68 |
| `ExecuteShell` | Eine Shell mit Programm und Parametern ausführen: | 118 |
| `MakeDirs` | Legt komplexe Directory an und löscht im Fehlerfall die von ihm angelegten Verzeichnisse auch wieder. | 141 |
| `Copy` | Äquivalent zu xcopy %Source% %Target% /s | 202 |
| `Delete` | Löscht Dateien und Unterverzeichnisse; auch mit Wildcards (Eine Art Staub- sauger, die man nach Partys braucht. Die auch kaputte Stühle mit aufsaugt.) | 294 |
| `Install` | Äquivalent zu xcopy %SourcePath%Source% %TargetPath%Target% /s | 420 |
| `HarderrHandler` | Fängt Diskettenfehler ab; siehe _harderr in c-doku | 441 |

### MESSAGES.C

`src/ALBION/OUTSIDE/BBSETUP/SRC/MESSAGES.C` – Installations- und Einrichtungsprogramm (Laufwerk wählen, Dateien kopieren, Soundkarte und Grafikmodus einstellen, INI schreiben).

Keine Funktionen (nur Daten).

### SCRIPT.C

`src/ALBION/OUTSIDE/BBSETUP/SRC/SCRIPT.C` – Installations- und Einrichtungsprogramm (Laufwerk wählen, Dateien kopieren, Soundkarte und Grafikmodus einstellen, INI schreiben).

| Funktion | Zweck | Zeile |
|---|---|---|
| `SKRIPT_Init` | Parameter ScriptFilename changed to ScriptFname - JH | 20 |
| `SCRIPT_GetTokenNumber` | Parameter TokenTable changed to TokenTab - JH | 174 |
| `SCRIPT_FindLabelLine` | Gibt die Zeilen des Labels zurück. (-1 für unbekannten Label) | 208 |
| `SCRIPT_ProcessScriptLine` | Eine Zeile aus dem Script bearbeiten und die nächste Zeilennummer zurückgeben | 235 |
| `SCRIPT_ParseScriptLine` | Zerlegt eine Zeile in seine Parameter; Gibt diese als UNCHAR** zurück sowie die Anzahl der Parameter als call-by-reference | 725 |
| `SCRIPT_GetIntParameter` | Konvertiert einen universellen String-Parameter in einen Integer | 806 |
| `SCRIPT_ScanForIfComplement` | Sucht nach ENDIF oder ELSE; gibt Zeilennummer zurück. | 825 |
| `SCRIPT_ScanForOpenIfs` | Gibt an wieviele IF's in Zeile x offen sind. Nötig für Sprünge. | 884 |

### SETUP.C

`src/ALBION/OUTSIDE/BBSETUP/SRC/SETUP.C` – Installations- und Einrichtungsprogramm (Laufwerk wählen, Dateien kopieren, Soundkarte und Grafikmodus einstellen, INI schreiben).

| Funktion | Zweck | Zeile |
|---|---|---|
| `main` | Hauptprogramm: | 17 |
| `Init_mouse_pointer` | Initialize a new mouse pointer. | 202 |
| `Write_chunk_name` | Write a four-character chunk name. | 263 |
| `Init_AIL_system` | Dummy function needed by BBSYSTEM. | 294 |
| `Exit_AIL_system` | Dummy function needed by BBSYSTEM. | 318 |

### TOKEN.C

`src/ALBION/OUTSIDE/BBSETUP/SRC/TOKEN.C` – Installations- und Einrichtungsprogramm (Laufwerk wählen, Dateien kopieren, Soundkarte und Grafikmodus einstellen, INI schreiben).

Keine Funktionen (nur Daten).

### VESA.C

`src/ALBION/OUTSIDE/BBSETUP/SRC/VESA.C` – Installations- und Einrichtungsprogramm (Laufwerk wählen, Dateien kopieren, Soundkarte und Grafikmodus einstellen, INI schreiben).

| Funktion | Zweck | Zeile |
|---|---|---|
| `D32DosMemAlloc` | Speicher im ersten Megabyte anlegen: | 45 |
| `VESA_IsAvailable` | Gibt TRUE zurück, falls ein VESA-Treiber installiert ist. | 62 |
| `VESA_SupportsMode` | Überprüft, ob der Videomodus verwendbar ist. TRUE=Ja | 109 |
| `VESA_IsInSupportList` | Schaut, ob ein Modus in der VESA-Supportlist ist. | 160 |
| `VESA_UpdateIni` | Überfüllt die VESA-INI-Datei mit Informationen | 173 |

### WINDOW.C

`src/ALBION/OUTSIDE/BBSETUP/SRC/WINDOW.C` – Installations- und Einrichtungsprogramm (Laufwerk wählen, Dateien kopieren, Soundkarte und Grafikmodus einstellen, INI schreiben).

| Funktion | Zweck | Zeile |
|---|---|---|
| `ErrorWindow` | Gibt ein rotes Fenster mit einem OK-Butten aus. | 12 |
| `InfoWindow` | Gibt ein normales Fenster mit einem OK-Button aus. | 29 |
| `GeneralWindow` | Gibt ein Error/Info-Style Fenster parametrisiert aus. | 46 |
| `AssertWindow` | Gibt ein YesNo-Fenster mit einem Text aus: | 186 |
| `GetButtonAnswer` | Verwaltet beliebig viele Buttons. Aufruf immer: - AnzButtons - AnzButtons * ┌ SILONG x1, y1, x2, y2 └ UNCHAR *KeyboardShortcuts | 362 |
| `GetMenuAnswer` | Verwaltet beliebig viele Buttons. | 391 |
| `SelectionWindow` | Zeigt ein Auswahlmenü an gibt die Zeilennummer des Verzweigungslabels zurück: | 587 |
| `aSelectionWindow` | Andreas Nitsche_7.9.95 | 754 |
| `SelectTargetDrive` | Erzeugt ein Menü mit den erlaubten Drives: | 1211 |
| `SelectCDDrive` | Erzeugt ein Menü mit den erlaubten Drives die ein CD-Rom seien könnten: | 1291 |
| `UserEntersString` | Läßt den Benutzer was eingeben, gibt Pointer austf atic Buffer zurück: | 1356 |
| `AdministrateProgressWindow` | Verwaltet das Balkenfenster für die Fortschrittsanzeige zum kopieren. 1 = Fenster eröffnen (Es darf noch nicht offen sein) 0 = Fenster aktualisieren (Es muß schon offen sein) -1 = Fenster schliessen (Es muß offen sein) | 1510 |
| `EasyPrintWindow` | Gibt einen Text parallel zum Kopieren aus. Verschwindet erst beim Aufruf mit Parameter NULL | 1618 |

## Weitere Quellen (nicht Teil von MAIN.EXE)

### ZOOMFUNC.C

`src/ALBION/OUTSIDE/RAINER/SRC/ZOOMFUNC/ZOOMFUNC.C` – Ältere Fassung der Zoomfunktionen (identisch im Zweck mit SRC/ZOOMFUNC).

| Funktion | Zweck | Zeile |
|---|---|---|
| `Put_masked_block` | Put a masked (transparent) block in an OPM through a temporary OPM. **R** | 40 |
| `Put_zoomed_block` | Put a zoomed block in an OPM. | 91 |
| `Put_zoomed_silhouette` | Put a single-colour silhouette of a zoomed block in an OPM. | 161 |
| `Put_zoomed_recoloured_silhouette` | Put a recoloured silhouette of a zoomed block in an OPM. | 230 |
| `Put_zoomed_recoloured_block` | Put a zoomed and recoloured block in an OPM. | 301 |
| `Put_zoomed_transparent_block` | Put a zoomed transparent block in an OPM. | 371 |

## Werkzeuge der Entwickler (nicht Teil von MAIN.EXE)

### CALCCOL.C

`src/ALBION/TOOLS/CALCCOL/CALCCOL.C` – Berechnet Transparenz- und Leuchttabellen aus einer Palette.

| Funktion | Zweck | Zeile |
|---|---|---|
| `main` | Main function of CALCCOL | 86 |
| `Load_palette_part` | Load part of a palette and copy it to the main palette. | 208 |
| `Calculate_transparency_table` | Calculate a transparency table. | 284 |
| `Calculate_luminance_table` | Calculate a luminance table. | 346 |
| `Calculate_transluminance_table` | Calculate a transluminance table. | 430 |

### COMPILE.C

`src/ALBION/TOOLS/COMPILER/COMPILE.C` – Packt Dateien zu einer XLD-Bibliothek.

| Funktion | Zweck | Zeile |
|---|---|---|
| `main` | Main function of XLD compiler. | 93 |
| `Get_subfile_data` | Get the paths and lengths of all subfiles. | 232 |
| `Compile_XLD_library` | Compile an XLD-library. | 362 |
| `Get_file_length` | Get the length of an opened file. | 674 |

### CONVEBES.C

`src/ALBION/TOOLS/CONVEBES/CONVEBES.C` – Wandelt LBM-Bilder um.

| Funktion | Zweck | Zeile |
|---|---|---|
| `main` | Main function of CONVEBES (convert an LBM picture). **R** | 63 |
| `Convert` | Unpack the LBM picture and write the converted graphics. **R** | 168 |
| `FindChunk` | Search a chunk in LBM file memory. | 316 |
| `Main_error_output_function` | Print an error message of the libraries. **R** | 371 |

### CONVLBM.C

`src/ALBION/TOOLS/CONVLBM/CONVLBM.C` – Wandelt LBM-Bilder um.

| Funktion | Zweck | Zeile |
|---|---|---|
| `main` | Main function of CONVLBM (convert an LBM picture). **R** | 63 |
| `Convert` | Unpack the LBM picture and write the converted graphics. **R** | 150 |
| `LBM_FindChunk` | Search a chunk in LBM file memory. | 298 |
| `Main_error_output_function` | Print an error message of the libraries. **R** | 353 |

### DUMP.C

`src/ALBION/TOOLS/DUMP/DUMP.C` – Gibt Dateiinhalte aus.

| Funktion | Zweck | Zeile |
|---|---|---|
| `main` | Main function of DUMP. **R** | 47 |

### MCP.C

`src/ALBION/TOOLS/MCP/MCP.C` – Startprogramm (Video zeigen, dann das Spiel starten).

| Funktion | Zweck | Zeile |
|---|---|---|
| `main` | Main function of MCP | 247 |
| `Start_game` | Start_the_game | 429 |
| `Show_video` | Show a video. | 589 |
| `OS_critical_error_handler` | Handle a critical OS error. | 660 |
| `Evaluate_program_arguments` | Evaluate program arguments. | 689 |
| `Parse_argument` | Parse an argument. | 754 |
| `Parse_value` | Parse a value. | 794 |
| `Init_data_paths` | Initialize data paths. | 820 |
| `Add_data_path` | Add a new data path. | 871 |
| `Select_data_path` | Select a data path. | 903 |
| `Search_second_data_path` | Look for a second data path. | 932 |
| `Check_CD` | Check if the second data path is the Albion CD. | 1015 |
| `Read_INI_variable` | Read a variable from the INI file. | 1063 |
| `Write_INI_variable` | Write a variable in the INI file. | 1225 |
| `File_exists` | Check if a file exists. | 1602 |
| `Directory_exists` | Check if a directory exists. | 1648 |
| `Change_directory` | Change the current directory. | 1688 |

### SHOWMEM.C

`src/ALBION/TOOLS/SHOWMEM/SHOWMEM.C` – Zeigt den freien Speicher an.

| Funktion | Zweck | Zeile |
|---|---|---|
| `main` | Main function of SHOWMEM | 101 |
| `BASEMEM_Init` | Initialize base memory. | 150 |
| `BASEMEM_Report` | Print a memory report. | 211 |
| `BASEMEM_FillMemByte` | Fills a buffer with a byte value. | 378 |

### XPAL.C

`src/ALBION/TOOLS/XPAL/XPAL.C` – Zieht die Palette aus einem LBM-Bild.

| Funktion | Zweck | Zeile |
|---|---|---|
| `main` | Main function of XPAL (extract the palette of an LBM file). **R** | 54 |
| `LBM_FindChunk` | Search a chunk in LBM file memory. | 167 |
| `Main_error_output_function` | Print an error message of the libraries. **R** | 222 |

