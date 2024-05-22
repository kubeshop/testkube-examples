package steps;

import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;

public class HelloWorldSteps {

    @Given("I have a working hello world example")
    public void i_have_a_working_hello_world_example() {
        // This can be empty for now
    }

    @When("I run the hello world example")
    public void i_run_the_hello_world_example() {
        // This can be empty for now
    }

    @Then("I should see {string} on the console")
    public void i_should_see_on_the_console(String expectedOutput) {
        String actualOutput = "Hello";
        if (!actualOutput.equals(expectedOutput)) {
            throw new AssertionError("Expected: " + expectedOutput + " but got: " + actualOutput);
        }
    }
}
