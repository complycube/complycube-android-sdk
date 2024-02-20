# ComplyCube Example App

This repository provides a pre-built UI that uses the ComplyCube SDK. It guides you through the ComplyCube identity verification process, which includes collecting client ID documents, proof of address documents, and biometric selfies.

> :information_source: Please get in touch with your **Account Manager** or **[support](https://support.complycube.com/hc/en-gb/requests/new)** to get access to our Mobile SDK.

## To run the app

1. Open the `gradle.properties` file and add your access credentials:

   ```gradle
   artifactory_user= "USERNAME"
   artifactory_password= "ENCRYPTED PASS"
   artifactory_contextUrl= https://complycuberepo.jfrog.io/artifactory
   ```

2. Synchronize your Gradle project to install the required dependencies.
3. [Create a Client ID](https://docs.complycube.com/documentation/guides/mobile-sdk-guide/mobile-sdk-integration-guide#id-2.-create-a-client).
4. [Generate an SDK token](https://docs.complycube.com/documentation/guides/mobile-sdk-guide/mobile-sdk-integration-guide#id-3.-generate-an-sdk-token).
5. In the `FirstFragment.kt` file, replace `CLIENT_ID` and `SDK_TOKEN` with the generated values from the previous steps.
6. Run the app.

> :information_source: If you're using an updated SDK version and run into any issues, please clear your `%USERPROFILE%\.gradle\caches` or `~/.gradle/caches` folder

## Integrating our SDK

For detailed instructions on integrating our SDK, please refer to our [integration guide](https://docs.complycube.com/documentation/guides/mobile-sdk-guide/mobile-sdk-integration-guide).

For an overview of our core platform and its multiple features, please refer to our [user guide](https://docs.complycube.com) or browse the [API reference](https://docs.complycube.com/api-reference) for fine-grained documentation of all our services.

## About ComplyCube

[ComplyCube](https://www.complycube.com/en) is a leading SaaS & API platform recognized for its AI-powered solutions in Identity Verification (IDV), Anti-Money Laundering (AML), and Know Your Customer (KYC) compliance. Serving a diverse range of sectors, including financial services, transport, healthcare, e-commerce, cryptocurrency, FinTech, telecoms, and more, ComplyCube has established itself as a major player in the IDV market globally.
<br>
<br>
The platform is ISO-certified and acclaimed for its rapid omnichannel integration capabilities and the comprehensive scope of its services. It offers a variety of Low/No-Code solutions, powerful API, Mobile SDKs, Client Libraries, and seamless CRM integrations.
