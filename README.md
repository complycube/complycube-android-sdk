## ComplyCube Example App

This repository provides a pre-built UI that uses the ComplyCube SDK. It guides you through the ComplyCube identity verification process, which includes collecting client ID documents, proof of address documents, and biometric selfies.

> :information_source: Please get in touch with your **Account Manager** or **[support](https://support.complycube.com/hc/en-gb/requests/new)** to get access to our Mobile SDK.

## To run the app 

### Add JFrog Credentials in `gradle.properties`

Start by adding your access credentials for the ComplyCube SDK repository to the `gradle.properties` file:

```gradle
artifactory_user= "USERNAME"
artifactory_password= "ENCRYPTED PASS"
artifactory_contextUrl= https://complycuberepo.jfrog.io/artifactory
```

and then synchronize your gradle to install the dependencies required.

### Generate SDK Token and Client ID and add to `FirstFragment.kt` and run the app
1. Navigate to `FirstFragment.kt`
2. [Create a Client ID](https://docs.complycube.com/documentation/guides/mobile-sdk-guide/mobile-sdk-integration-guide#id-2.-create-a-client) and replace `Enter ClientID here` with your Client ID
3. [Create an SDK Token](https://docs.complycube.com/documentation/guides/mobile-sdk-guide/mobile-sdk-integration-guide#id-3.-generate-an-sdk-token) and replace `Enter JWT Token here` with your SDK Token
4. Run the app


## Integrating our SDK

For detailed instructions on integrating our SDK, please refer to our [integration guide](https://docs.complycube.com/documentation/guides/mobile-sdk-guide/mobile-sdk-integration-guide).

For an overview of our core platform and its multiple features, please refer to our [user guide](https://doc.complycube.com) or browse the [API reference](https://docs.complycube.com/api-reference) for fine-grained documentation of all our services.