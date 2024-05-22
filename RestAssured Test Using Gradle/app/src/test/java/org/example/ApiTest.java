package org.example;

import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.junit.jupiter.api.Test;

import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

public class ApiTest {

    @Test
    public void testGetEndpoint() {
        RestAssured.baseURI = "https://jsonplaceholder.typicode.com";
        
        given().
            when().
            get("/posts/1").
            then().
            statusCode(200).
            body("userId", equalTo(1)).
            body("id", equalTo(1)).
            body("title", not(empty())).
            body("body", not(empty()));
    }
}
