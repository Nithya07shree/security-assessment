/**
 * What this file doeS?
 *    Makes HTTP calls from Java Spring Boot backend to the Python Flask AI service running on port 5000
 *    Every method returns null on any error so the backend never crashes when AI service is unavailable
 * 
 * Using RestTemplate as explicitly mentioned in the tech stack, supports the synchronous Spring Boot app in the backend
*/

/**
 * HOW TO USE THIS IN A SERVICE 
 * - calling from ControlService.java
 * 
 * @Service
 * public class ControlService {
 *  private final AiServiceClient aiServiceClient;
 *  private final ControlRepository controlRepository;
 * 
 *  public ControlService(AiServiceClient aiServiceClient, ControlRepository controlRepository){
 *      this.aiServiceClient = aiServiceClient;
 *      this.controlRepository = controlRepository;
 *  }
 *  
 *  public Control createControl(ControlDto dto) {
 *         Control control = new Control();
 *         control.setTitle(dto.getTitle());
 *         control.setDescription(dto.getDescription());
 *
 *         // Call AI — but handle null gracefully
 *         // AI being down should never prevent record creation
 *         Map<String, Object> aiResult =
 *             aiServiceClient.describe(dto.getDescription());
 *
 *         if (aiResult != null) {
 *             // AI responded — attach the result
 *             control.setAiDescription(
 *                 (String) aiResult.get("description")
 *             );
 *         } else {
 *             // AI unavailable — set a default, do not throw
 *             control.setAiDescription("AI analysis pending");
 *         }
 *
 *         return controlRepository.save(control);
 *     }
 * }
*/

package com.internship.tool.config;
 
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
 
import java.time.Duration;
import java.util.List;
import java.util.Map;


@Component
public class AiServiceClient {
    private static final Logger logger = LoggerFactory.getLogger(AiServiceClient.class);

    @Value("${ai.service.url:http:http://ai-service:5000}")
    private String aiServiceUrl;

    // the RestTemplate instance is configured once in the constructor with a 10 second timeout on both connection and read.
    // connect timeout - how long to wait to establish TCP connection
    // read timeout - how long to wait for the response after connecting
    private final RestTemplate restTemplate;

    public AiServiceClient(RestTemplateBuilder builder){
        this.restTemplate = builder.connectTimeout(Duration.ofSeconds(10)).readTimeout(Duration.ofSeconds(10)).build();
    }

    // helper methods

    /**  A standard HttpEntity with JSON content type header
     * Every POST request to the Flask service needs Content-Type: application/json
     * otherwise Flask's request.get_json() returns None.
    */

    private HttpEntity<Map<String,Object>> buildRequest(Map<String,Object>body){
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        return new HttpEntity<>(body, headers);
    }

   /**
    * Core POST method used by all endpoint callers below
    * Makes actual HTTP call, handles all errrors, returns null on failure
    * It basically :
    * - constructs the URL: joins base url with endpoint
    * - builds request: sets headers to application/json
    * - restTemplate.exchange: actually sends the POST request
    * - has error handling
    * - returns null if anything goes wrong
    */
    @SuppressWarnings("unchecked")
    private Map<String, Object> post(String endpoint, Map<String, Object> body){
        String url = aiServiceUrl + endpoint;
        try {
            HttpEntity<Map<String, Object>> request = buildRequest(body);
            ResponseEntity<Map> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    request,
                    Map.class
            );
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null){
                return response.getBody();
            }
            logger.warn("AI service returned non-2xx status: {} for endpoint: {}", response.getStatusCode(), endpoint);
            return null;
        }
        catch (RestClientException e) {
            // catches: connection refused, timeout, 4xx errors, 5xx errors
            logger.warn("AI service call failed for endpoint: {} | Reason: {}",endpoint, e.getMessage());
            return null;
        }
        catch (Exception e){
            logger.error("Unexpected error calling AI service endpoint: {} | Error: {}", endpoint, e.getMessage(), e);
            return null;
        }
    }

    // PUBLIC ENDPOINT METHODS

    // POST /describe
    public Map<String, Object> describe(String text){
        if (text == null || text.isBlank()) {
            logger.warn("describe() called with empty text — skipping AI call");
            return null;
        }
        return post("/describe", Map.of("text", text));
    }

    // POST /recommend
    public Map<String, Object> recommend(String text) {
        if (text == null || text.isBlank()) {
            logger.warn("recommend() called with empty text — skipping AI call");
            return null;
        }
        return post("/recommend", Map.of("text", text));
    }

    // POST /categorise
    public Map<String, Object> categorise(String text) {
        if (text == null || text.isBlank()) {
            logger.warn("categorise() called with empty text — skipping AI call");
            return null;
        }
        return post("/categorise", Map.of("text", text));
    }

    // POST /generate-report
    public Map<String, Object> generateReport(String text, String context) {
        if (text == null || text.isBlank()) {
            logger.warn("generateReport() called with empty text — skipping AI call");
            return null;
        }
        String safeContext = context != null ? context : "";
        return post("/generate-report", Map.of("text", text, "context", safeContext));
    }

    // POST /query
    public Map<String, Object> query(String question) {
        if (question == null || question.isBlank()) {
            logger.warn("query() called with empty question — skipping AI call");
            return null;
        }
        return post("/query", Map.of("question", question));
    }

    // POST /analyse-document
    public Map<String, Object> analyseDocument(String text) {
        if (text == null || text.isBlank()) {
            logger.warn("analyseDocument() called with empty text — skipping AI call");
            return null;
        }
        return post("/analyse-document", Map.of("text", text));
    }

    // GET /health
    @SuppressWarnings("unchecked")
    public Map<String, Object> health() {
        String url = aiServiceUrl + "/health";
        try {
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
 
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            }
 
            logger.warn("AI service health check returned non-2xx: {}",
                    response.getStatusCode());
            return null;
 
        } catch (RestClientException e) {
            logger.warn("AI service health check failed — service may be starting up: {}",
                    e.getMessage());
            return null;
        } catch (Exception e) {
            logger.error("Unexpected error during AI service health check: {}",
                    e.getMessage(), e);
            return null;
        }
    }

}