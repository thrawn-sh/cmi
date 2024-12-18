CREATE OR REPLACE VIEW cmi_view AS
SELECT 
    time AS time,                                                                    -- time stamp
    analog_00 AS tank_top,                                                           -- hot water tank top
    ((analog_00 + analog_01) / 2) AS tank_middle,                                    -- hot water tank middle
    analog_01 AS hot_tank_bottom,                                                    -- hot water tank bottom
    analog_04 AS temperature,                                                        -- outside temperature
    analog_02 AS hc_flow,                                                            -- heat circuit flow temperature
    analog_09 AS hc_returnflow,                                                      -- heat circuit return flow temperature
    analog_21 AS hc_mixer,                                                           -- heat circuit mixer
    digital_13 AS hc_pump,                                                           -- heat circuit pump
    analog_07 AS hp_flow,                                                            -- heat pump flow temperature
    analog_08 AS hp_returnflow,                                                      -- heat pump return flow temperature
    digital_04 AS defrost,                                                           -- heat pump is defrosting
    (digital_19 OR digital_20 OR digital_21 OR digital_22 OR digital_23) AS heating, -- heat pump is heating
FROM cmi;
