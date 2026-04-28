/**
 * What this file doeS?
 *    Makes HTTP calls from Java Spring Boot backend to the Python Flask AI service running on port 5000
 *    Every method returns null on any error so the backend never crashes when AI service is unavailable
 * 
 * Using RestTemplate as explicitly mentioned in the tech stack, supports the synchronous Spring Boot app in the backend
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
}