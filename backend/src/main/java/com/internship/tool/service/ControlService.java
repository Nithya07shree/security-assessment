/**
 * ControlService.java
 * 
 * This file contains the ControlService class, which is responsible for creating and enriching controls with AI.
 * It uses the AiServiceClient to call the AI service and get the AI analysis of the control.
 * It then saves the control to the database.
 * 
 * Immediately after create, the frontend shows:
 * {
  "title":"Password Policy",
  "aiDescription":"AI analysis pending",
  "aiStatus":"PENDING"
}
 * To test, run flask: python app.py, run spring, create a control, check fatabase
 */

package com.internship.tool.service;

import com.internship.tool.config.AiServiceClient;
import com.internship.tool.dto.ControlDto;
import com.internship.tool.entity.Control;
import com.internship.tool.repository.ControlRepository;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.Optional;

@Service
public class ControlService {

    private static final Logger logger =
            LoggerFactory.getLogger(ControlService.class);

    private final ControlRepository controlRepository;
    private final AiServiceClient aiServiceClient;

    public ControlService(
            ControlRepository controlRepository,
            AiServiceClient aiServiceClient
    ) {
        this.controlRepository = controlRepository;
        this.aiServiceClient = aiServiceClient;
    }

    /*
     * Step 1:
     * save immediately
     *
     * Step 2:
     * trigger AI in background
     */
    public Control createControl(ControlDto dto) {

        Control control = new Control();

        control.setTitle(dto.getTitle());
        control.setDescription(dto.getDescription());

        /*
         * show frontend something immediately
         */
        control.setAiDescription("AI analysis pending");
        control.setAiStatus("PENDING");

        Control saved =
                controlRepository.save(control);

        /*
         * background AI processing
         */
        enrichWithAi(saved.getId());

        return saved;
    }

    /*
     * background thread
     *
     * AI outage must never crash backend
     */
    @Async
    public void enrichWithAi(Long controlId) {

        try {

            Optional<Control> optionalControl =
                    controlRepository.findById(controlId);

            if (optionalControl.isEmpty()) {
                logger.warn(
                        "Control not found for AI enrichment: {}",
                        controlId
                );
                return;
            }

            Control control =
                    optionalControl.get();

            Map<String, Object> aiResult =
                    aiServiceClient.describe(
                            control.getDescription()
                    );

            /*
             * Flask unavailable
             */
            if (aiResult == null) {

                control.setAiDescription(
                        "AI analysis unavailable"
                );

                control.setAiStatus(
                        "FAILED"
                );

                controlRepository.save(control);

                logger.warn(
                        "AI service unavailable for control: {}",
                        controlId
                );

                return;
            }

            /*
             * success
             */
            String description =
                    (String) aiResult.getOrDefault(
                            "description",
                            "No analysis returned"
                    );

            control.setAiDescription(
                    description
            );

            control.setAiStatus(
                    "COMPLETED"
            );

            controlRepository.save(control);

            logger.info(
                    "AI enrichment completed for control: {}",
                    controlId
            );

        }
        catch (Exception e) {

            logger.error(
                    "AI enrichment failed for control: {}",
                    controlId,
                    e
            );

            try {

                controlRepository.findById(controlId)
                        .ifPresent(control -> {

                            control.setAiDescription(
                                    "AI analysis failed"
                            );

                            control.setAiStatus(
                                    "FAILED"
                            );

                            controlRepository.save(
                                    control
                            );
                        });

            }
            catch (Exception ignored) {
            }
        }
    }
}