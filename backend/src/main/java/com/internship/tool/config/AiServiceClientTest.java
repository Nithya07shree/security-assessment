/**
 * Tests for AiServiceClient — verifies that:
 * 1. Successful AI responses are returned correctly
 * 2. Null is returned gracefully when AI service is unavailable
 * 3. Null is returned gracefully on timeout
 * 4. Empty input is handled without making a network call
 * 
 * Java Developer 1: Add this dependency to pom.xml if not present:
 *   <dependency>
 *       <groupId>org.mockito</groupId>
 *       <artifactId>mockito-core</artifactId>
 *       <scope>test</scope>
 *   </dependency>
 */

package com.internship.tool.config;
 
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.*;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;
 
import java.util.Map;
 
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

class AiServiceClientTest {
 
    private AiServiceClient aiServiceClient;
    private RestTemplate restTemplate;
 
    @BeforeEach
    void setUp() {
        // Create a mock RestTemplate — does not make real HTTP calls
        restTemplate = mock(RestTemplate.class);
 
        // Create RestTemplateBuilder mock that returns our mocked RestTemplate
        RestTemplateBuilder builder = mock(RestTemplateBuilder.class);
        when(builder.connectTimeout(any())).thenReturn(builder);
        when(builder.readTimeout(any())).thenReturn(builder);
        when(builder.build()).thenReturn(restTemplate);
 
        aiServiceClient = new AiServiceClient(builder);
 
        // Set the private aiServiceUrl field
        ReflectionTestUtils.setField(
                aiServiceClient,
                "aiServiceUrl",
                "http://localhost:5000"
        );
    }

    // test /decribe
    @Test
    void describe_returnsAiResponse_whenServiceAvailable() {
        // Arrange — mock a successful AI response
        Map<String, Object> mockResponse = Map.of(
                "description", "This control ensures MFA is enforced",
                "generated_at", "2026-04-17T10:00:00Z"
        );
        ResponseEntity<Map> responseEntity =
                new ResponseEntity<>(mockResponse, HttpStatus.OK);
 
        when(restTemplate.exchange(
                contains("/describe"),
                eq(HttpMethod.POST),
                any(HttpEntity.class),
                eq(Map.class)
        )).thenReturn(responseEntity);
 
        // Act
        Map<String, Object> result = aiServiceClient.describe("MFA control description");
 
        // Assert
        assertNotNull(result);
        assertEquals("This control ensures MFA is enforced", result.get("description"));
    }

    @Test
    void describe_returnsNull_whenServiceUnavailable() {
        // Arrange — simulate connection refused
        when(restTemplate.exchange(
                contains("/describe"),
                eq(HttpMethod.POST),
                any(HttpEntity.class),
                eq(Map.class)
        )).thenThrow(new ResourceAccessException("Connection refused"));
 
        // Act
        Map<String, Object> result = aiServiceClient.describe("some text");
 
        // Assert — must return null, not throw an exception
        assertNull(result);
    }
 
    @Test
    void describe_returnsNull_whenTextIsEmpty() {
        // Act — empty string
        Map<String, Object> result1 = aiServiceClient.describe("");
        // Act — null
        Map<String, Object> result2 = aiServiceClient.describe(null);
        // Act — whitespace only
        Map<String, Object> result3 = aiServiceClient.describe("   ");
 
        // Assert — all return null without making a network call
        assertNull(result1);
        assertNull(result2);
        assertNull(result3);
 
        // Verify no HTTP call was made for empty input
        verifyNoInteractions(restTemplate);
    }

    // recommend() tests

    @Test
    void recommend_returnsRecommendations_whenServiceAvailable() {
        // Arrange
        Map<String, Object> mockResponse = Map.of(
                "recommendations", java.util.List.of(
                        Map.of("action_type", "IMPLEMENT",
                               "description", "Enable MFA on all accounts",
                               "priority", "HIGH")
                )
        );
        ResponseEntity<Map> responseEntity =
                new ResponseEntity<>(mockResponse, HttpStatus.OK);
 
        when(restTemplate.exchange(
                contains("/recommend"),
                eq(HttpMethod.POST),
                any(HttpEntity.class),
                eq(Map.class)
        )).thenReturn(responseEntity);
 
        // Act
        Map<String, Object> result = aiServiceClient.recommend("MFA not implemented");
 
        // Assert
        assertNotNull(result);
        assertNotNull(result.get("recommendations"));
    }
 
    @Test
    void recommend_returnsNull_onTimeout() {
        // Arrange — simulate read timeout
        when(restTemplate.exchange(
                contains("/recommend"),
                eq(HttpMethod.POST),
                any(HttpEntity.class),
                eq(Map.class)
        )).thenThrow(new ResourceAccessException("Read timed out"));
 
        // Act
        Map<String, Object> result = aiServiceClient.recommend("some text");
 
        // Assert
        assertNull(result);
    }
 
    // generateReport() tests
    
    @Test
    void generateReport_returnsNull_whenTextIsEmpty() {
        Map<String, Object> result = aiServiceClient.generateReport("", "some context");
        assertNull(result);
        verifyNoInteractions(restTemplate);
    }
 
    @Test
    void generateReport_handlesNullContext_gracefully() {
        // Arrange — null context should not cause NullPointerException
        Map<String, Object> mockResponse = Map.of("title", "Security Report");
        ResponseEntity<Map> responseEntity =
                new ResponseEntity<>(mockResponse, HttpStatus.OK);
 
        when(restTemplate.exchange(
                contains("/generate-report"),
                eq(HttpMethod.POST),
                any(HttpEntity.class),
                eq(Map.class)
        )).thenReturn(responseEntity);
 
        // Act — passing null context should work fine
        Map<String, Object> result =
                aiServiceClient.generateReport("control summary text", null);
 
        // Assert
        assertNotNull(result);
    }
 
    // health() tests
       
    @Test
    void health_returnsHealthData_whenServiceRunning() {
        // Arrange
        Map<String, Object> mockHealth = Map.of(
                "status", "ok",
                "model", "llama-3.3-70b",
                "chroma_doc_count", 10
        );
        ResponseEntity<Map> responseEntity =
                new ResponseEntity<>(mockHealth, HttpStatus.OK);
 
        when(restTemplate.getForEntity(
                contains("/health"),
                eq(Map.class)
        )).thenReturn(responseEntity);
 
        // Act
        Map<String, Object> result = aiServiceClient.health();
 
        // Assert
        assertNotNull(result);
        assertEquals("ok", result.get("status"));
    }
 
    @Test
    void health_returnsNull_whenServiceDown() {
        // Arrange
        when(restTemplate.getForEntity(
                contains("/health"),
                eq(Map.class)
        )).thenThrow(new ResourceAccessException("Connection refused"));
 
        // Act
        Map<String, Object> result = aiServiceClient.health();
 
        // Assert
        assertNull(result);
    }
 
    // query() tests
    
    @Test
    void query_returnsAnswer_whenServiceAvailable() {
        // Arrange
        Map<String, Object> mockResponse = Map.of(
                "answer", "MFA should be enforced using TOTP",
                "sources", java.util.List.of("NIST SP 800-63B", "ISO 27001")
        );
        ResponseEntity<Map> responseEntity =
                new ResponseEntity<>(mockResponse, HttpStatus.OK);
 
        when(restTemplate.exchange(
                contains("/query"),
                eq(HttpMethod.POST),
                any(HttpEntity.class),
                eq(Map.class)
        )).thenReturn(responseEntity);
 
        // Act
        Map<String, Object> result =
                aiServiceClient.query("What is best practice for MFA?");
 
        // Assert
        assertNotNull(result);
        assertNotNull(result.get("answer"));
        assertNotNull(result.get("sources"));
    }
 
    @Test
    void query_returnsNull_whenQuestionIsBlank() {
        Map<String, Object> result = aiServiceClient.query("   ");
        assertNull(result);
        verifyNoInteractions(restTemplate);
    }

}