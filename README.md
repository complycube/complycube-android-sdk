# ComplyCube Android SDK

The ComplyCube Android SDK makes it quick and easy to build a frictionless customer onboarding and biometric re-authentication experience in your Android app. We provide powerful, smart, and customizable UI screens that can be used out-of-the-box to capture the data you need for identity verification.

> Please get in touch with your **Account Manger** or **[support](https://support.complycube.com/hc/en-gb/requests/new)** to get access to our Mobile SDK.

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Getting started](#getting-started)
  * [1. Installing the SDK](#1-installing-the-sdk)
  * [2. Creating a client](#2-creating-a-client)
    + [Example request](#example-request)
    + [Example response](#example-response)
  * [3. Creating an SDK token](#3-creating-an-sdk-token)
    + [Example request](#example-request-1)
    + [Example response](#example-response-1)
  * [4. Initialize a flow with default settings](#4-initialize-a-flow-with-default-settings)
  * [5. Perform checks](#5-perform-checks)
    + [Example request](#example-request-2)
  * [6. Setup webhooks and retrieve results](#6-setup-webhooks-and-retrieve-results)
- [Customization](#customization)
  * [Customizing stages](#customizing-stages)
      - [Welcome stage](#welcome-stage)
      - [Consent stage](#consent-stage)
      - [Document stage](#document-stage)
      - [Selfie photo and video stage](#selfie-photo-and-video-stage)
      - [Proof of Address](#proof-of-address)
  * [Customizing appearance](#customizing-appearance)
  * [Result handling](#result-handling)
  * [Error handling](#error-handling)
    + [Runtime errors](#runtime-errors)
    + [Invalid configuration exceptions](#invalid-configuration-exceptions)
  * [Localization](#localization)
  * [Going live](#going-live)
  * [Additional info](#additional-info)

## Features

<img src="https://assets.complycube.com/images/complycube-android-sdk-github.jpg" alt="ComplyCube Android SDK illustrations"/>

**Native & intuitive UI**: We provide mobile-native screens that guide your customers in capturing their selfies, video recordings, government-issued IDs (such as passports, driving licenses, and residence permits), and proof of address documents (bank statements and utility bills)

**Liveness**: Our market-leading liveness detection provides accurate and extremely fast presence detection on your customers' selfies (3D Passive and Active) and documents to prevent fraud and protect your business. It detects and deters several spoofing vectors, including **printed photo attacks**, **printed mask attacks**, **video replay attacks**, and **3D mask attacks**.

**Auto-capture**: Our UI screens attempt to auto-capture your customer's documents and selfies and run quality checks to ensure that only legible captures are processed by our authentication engine.

**Branding & customization**: You can customize the experience by adding your brand colors and your own text. Furthermore, screens can be added and removed.

**ComplyCube API**: Our [REST API](https://docs.complycube.com/api-reference) can be used to build entirely custom flows on top of this native mobile UI layer. We offer backend SDK libraries ([Node.js](https://www.npmjs.com/package/@complycube/api), [PHP](https://github.com/complycube/complycube-php), [Python](https://pypi.org/project/complycube/), and [.NET](https://www.nuget.org/packages/Complycube/)) to facilitate custom integrations.

**Localized**: We offer multiple localization options to fit your customer needs.

**Secure**: Our GPDR, CCPA, and ISO-certified platform ensure secure and data privacy-compliant end-to-end capture.

## Requirements

* Android 5.0 (API level 21) and above
* AndroidX
* Kotlin 1.5+

## Getting started

Get started with our [user guide](https://doc.complycube.com) for an overview of our core platform and its multiple features, or browse the [API reference](https://docs.complycube.com/api-reference) for fine-grained documentation of all our services.

<p align="center">
<img src="https://2744061101-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F-M7DZEw-mdC0afAU1zYm%2Fuploads%2FXpYpd1Aju7dRruchnDLc%2Fdocumentation-Mobile%20SDK-min.png?alt=media&token=77aa65b2-da20-44eb-b458-ac7bd2d0586b" alt="ComplyCube Mobile SDK integration flow"/>
    Mobile SDK integration flow
</p>


### 1. Installing the SDK

Start by adding your access credentials for the ComplyCube SDK repository to the `gradle.properties` file of your **mobile app**:

```gradle
artifactory_user= "USERNAME"
artifactory_password= "ENCRYPTED PASS"
artifactory_contextUrl= https://complycuberepo.jfrog.io/artifactory
```

Then update your application `build.gradle` file with the ComplyCube SDK repository maven settings and SDK dependency:

```gradle
plugins {
    ...
    id "com.jfrog.artifactory"
}

repositories {
    mavenCentral()
    google()
    artifactory {
        contextUrl = "${artifactory_contextUrl}"  
        resolve {
            repository {
                repoKey = 'complycube-sdk-gradle-release-local'
                username = "${artifactory_user}"
                password = "${artifactory_password}"
                maven = true

            }
        }
    }
}

dependencies {
    implementation "com.complycube:sdk:+"
    ...
}
```

### 2. Creating a client

Before launching the SDK, your app must first [create a client](https://docs.complycube.com/api-reference/clients/create-a-client) using the ComplyCube API.

A client represents the individual on whom you need to perform identity verification checks on. A client is required to generate an SDK token. 

This must be done on your **mobile app backend** server.

#### Example request

```bash
curl -X POST https://api.complycube.com/v1/clients \
     -H 'Authorization: <YOUR_API_KEY>' \
     -H 'Content-Type: application/json' \
     -d '{  "type": "person",
            "email": "john.doe@example.com",
            "personDetails":{
                "firstName": "Jane",
                "lastName" :"Doe"
            }
         }'
```

#### Example response
The response will contain an id (the Client ID). It is required for the next step.

```json
{
    "id": "5eb04fcd0f3e360008035eb1",
    "type": "person",
    "email": "john.doe@example.com",
    "personDetails": {
        "firstName": "John",
        "lastName": "Doe",
    },
    "createdAt": "2023-01-01T17:24:29.146Z",
    "updatedAt": "2023-01-01T17:24:29.146Z"
}
```

### 3. Creating an SDK token

**SDK Tokens** enable clients to securely send personal data from your **mobile app** to ComplyCube.
[To learn more about our SDK Token endpoint](https://docs.complycube.com/api-reference/other-resources/tokens).

> You must generate a new token each time you initialise the ComplyCube Web SDK.

#### Example request

```bash
curl -X POST https://api.complycube.com/v1/tokens \
     -H 'Authorization: <YOUR_API_KEY>' \
     -H 'Content-Type: application/json' \
     -d '{
          	"clientId":"CLIENT_ID",
          	"appId": "com.complycube.sampleapp"
         }'
```

#### Example response
```json
{
    "token": "<CLIENT_TOKEN>"
}
```

### 4. Initialize a flow with default settings

Now you can initialize a flow with the default settings.

```kotlin
var complycubeFlow = ComplyCubeSdk.Builder(this, callback= ...)
                        .withSDKToken("SDK_Token")
                        
complycubeFlow.start()
```

### 5. Perform checks

Using the `StageResults` returned by the flow, you can trigger your **mobile backend** to run the necessary checks on your client. 

For example, use the properties:

* `StageResult.Document.Id` to run a document check
* `StageResult.Document.Id` and `StageResult.LivePhoto.Id` to run an identity check

#### Example request

```curl
curl -X POST https://api.complycube.com/v1/checks \
     -H 'Authorization: <YOUR_API_KEY>' \
     -H 'Content-Type: application/json' \
     -d '{
            "clientId":"CLIENT_ID",
            "type": "document_check",
            "documentId":"DOCUMENT_ID"
         }'
```

### 6. Setup webhooks and retrieve results

> Our checks are asynchronous, and all results and event notifications are done via webhooks.

Follow our [webhook guide](https://docs.complycube.com/documentation/guides/webhooks) for a step-by-step walkthrough.

Your **mobile backend** can retrieve all check results using our API.

## Customization

### Customizing stages

Each stage in the flow can be customized to create the ideal journey for your clients.

##### Welcome stage

This screen allows you to set a custom title and informative message to inform your customers about the KYC/identity verification process in more detail.


``` kotlin
var welcomeStage = Welcome( title = "Custom Screen Title", message = "Custom welcome message")
```

> The welcome stage will always default to show as the first screen. 

##### Consent stage

You can optionally add this stage to enforce explicit consent collection before the client can progress in the flow. The consent screen allows you to set a custom title.

``` kotlin
var consentStage = Consent( title = "Custom Consent Screen Title")
```

##### Document stage

This stage allows clients to select the type of identity document they would like to submit. You can customize these screens to:

* Limit the scope of document types the client can select e.g. Passport only.
* Set the document issuing countries they are allowed for each document type.
* Add or remove automated capture using smart assistance.
* Show or hide the instruction screens before capture.
* Set a retry limit to allow clients to progress the journey regardless of capture quality.

> If you provide only one document type, the document type selection screen will be skipped. If you provide only a single country for a given document type, the country selection screen will be skipped.

By enabling or disabling guidance, you can remove the information screens shown before camera captures. You should only consider omitting this if you have clearly informed your customer of the capture steps required.

> :warning: Please note the `retryLimit` you set here will take precedence over the retry limit that has been set globally in the [developer console](https://portal.complycube.com/automations).

``` kotlin
var documentStage = Document (
            Passport(),DrivingLicence((GB)), 
            isGuidanceEnabled = true,
            retryLimit = 3
        )
```

If you want to set the countries across all document types (apart from passports), you can set the top-level country lists at the flow level.

```kotlin
var complycubeFlow = ComplyCubeSdk.Builder(this, callback= ...)
                        .withCountries(Country.GB, Country.US)
                        ....
```

##### Selfie photo and video stage
You can request a selfie photo ([live photo](https://docs.complycube.com/api-reference/live-photos)) capture or video ([live video](https://docs.complycube.com/api-reference/live-videos)) capture from your customer. 

``` kotlin
var selfiePhoto = SelfiePhoto(isGuidanceEnabled = true, isMLAssistantEnabled = false)
```
or

``` kotlin
var selfieVideo = SelfieVideo(isGuidanceEnabled = true, isMLAssistantEnabled = false)
```

> :warning: If you attempt to add both, the SDK will throw a ComplyCubeSDKException error stating `ConflictingStages`.

##### Proof of Address

When requesting a proof of address document, you can set the allowed document type and whether the client can upload the document. When `useLiveCaptureOnly` is set to false, the client will be forced to perform a live capture.

```kotlin
var poaStage = ProofOfAddress(UtilityBill(),BankStatement(), 
            useLiveCaptureOnly = false, 
            ...
        )
```

### Customizing appearance

The SDK allows you to set colors to match your existing application or brand. You can customize the colors by setting the relevant values when building your flow. 

```kotlin
complycubeFlow.withCustomColors(customColors = SdkColors( primaryButtonColor = Color.RED))
```

| Appearence property | Description |
| --- | ----------- |
| ```primaryButtonColor``` | Primary action button background color |
| ```primaryButtonTextColor``` | Primary action button text color |
| ```primaryButtonBorderColor``` | Primary action button border color |
| ```secondaryButtonColor``` | Secondary button background color |
| ```secondaryButtonTextColor``` | Secondary action button text color |
| ```secondaryButtonBorderColor``` | Secondary action button border color |
| ```documentSelectorColor``` | Document type selection button color |
| ```documentSelectorBorderColor``` | Document type selection button border color |
| ```documentSelectorIconColor``` | Document type icon color |
| ```documentSelectorTitleTextColor``` | Document type title text color |
| ```documentSelectorDescriptionTextColor``` | Document type description text color |
| ```bodyTextColor``` | Screen body text color |
| ```headingTextColor``` | Title heading text color |
| ```subheadingTextColor``` | Subheading text color |

### Result handling

When initializing your client flow, you will need to register a result handler to process the outcome of the flow.

```kotlin
var complycubeFlow = ComplyCubeSdk.Builder(this) { flowResult ->
            when(flowResult){
                is ComplyCubeResult.Error -> // Your callback code here
                is ComplyCubeResult.Success -> // Your callback code here
                is ComplyCubeResult.Canceled -> // Your callback code here
            }
        }
```

When the outcome is a `Result.Success`, you can start creating [check requests](https://docs.complycube.com/api-reference/checks/create-a-check) using the captured data. The IDs of the uploaded resources are returned in the `stages` property.

For example, our default flow, which include an Identity Document, Selfie (Live Photo), and Proof of Address, would have a stages collection that looks like this.

```kotlin
    (StageResult.Document.Id, StageResult.LivePhoto.Id, StageResult.ProofOfAddress.Id)
```

### Error handling

#### Runtime errors

If the SDK experiences any issues, the error callback will be triggered with one of the following exceptions.

| Error | Description |
| --- | ----------- |
| ```ComplyCubeResult.Error.NotAuthorised``` | The SDK has attempted a request to an endpoint you are not authorized to use.|
| ```ComplyCubeResult.Error.TokenExpired``` | The token used to initialize the SDK has expired. Create a new SDK token and restart the flow. |
| ```ComplyCubeResult.Error.Unknown``` | An unexpected error has occured. If this keeps occurring, let us know about it. |

#### Invalid configuration exceptions 

If the SDK is misconfigured, the flow builder will raise an exception when attempting to launch.

| Error | Description |
| --- | ----------- |
| ```ComplyCubeSDKException.MissingToken``` | Attempted to launch the SDK without setting the SDK token. |
| ```ComplyCubeSDKException.DuplicateStages``` | Launch configuration contains duplicate stages. |
| ```ComplyCubeSDKException.ConflictingStages``` | Configuration contains both a Live Video and Live Photo stage.|
| ```ComplyCubeSDKException.InvalidDeviceSetup``` | User device has been flagged as jailbroken |
| ```ComplyCubeSDKException.StageSettingConflict``` | If `useLiveCaptureOnly` is false, guidance must be enabled. |
| ```ComplyCubeSDKException.Unknown``` | An unexpected error has occured. If this keeps occurring, let us know about it. |

### Localization

The SDK provides the following language support

* English - `en` :uk:
* French - `fr` :fr:
* German - `de` :de:
* Italian - `it` :it:
* Spanish - `es` :es:

### Going live

Check out our handy [integration checklist here](https://docs.complycube.com/documentation/guides/integration-checklist) before you go live.

### Additional info

You can find our full [API reference here](https://docs.complycube.com/api-reference), and our guides and example flows can be found [here](https://docs.complycube.com/documentation/).
