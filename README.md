# ComplyCube Android SDK

The ComplyCube Android SDK makes it quick and easy to build a frictionless customer onboarding and biometric re-authentication experience in your Android app. We provide powerful, smart, and customizable UI screens that can be used out-of-the-box to capture the data you need for identity verification.

> :information_source: Please get in touch with your **Account Manager** or **[support](https://support.complycube.com/hc/en-gb/requests/new)** to get access to our Mobile SDK.

> :warning: If you were on our previous generation SDK (deprecated), please migrate to this one. Get in touch with support if you have any questions.

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Getting started](#getting-started)
  - [1. Installing the SDK](#1-installing-the-sdk)
  - [2. Creating a client](#2-creating-a-client)
    - [Example request](#example-request)
    - [Example response](#example-response)
  - [3. Creating an SDK token](#3-creating-an-sdk-token)
    - [Example request](#example-request-1)
    - [Example response](#example-response-1)
  - [4. Initialize an SDK flow](#4-initialize-an-sdk-flow)
  - [5. Perform checks](#5-perform-checks)
    - [Example request](#example-request-2)
  - [6. Setup webhooks and retrieve results](#6-setup-webhooks-and-retrieve-results)
- [Customization](#customization)
  - [Stages](#stages)
    - [Welcome stage](#welcome-stage)
    - [Consent stage](#consent-stage)
    - [Document stage](#document-stage)
    - [Selfie photo and video stage](#selfie-photo-and-video-stage)
    - [Proof of address stage](#proof-of-address-stage)
    - [Completion stage](#completion-stage)
  - [Look and feel](#look-and-feel)
  - [Localization](#localization)
  - [Callback Handling](#callback-handling)
    - [Result handling](#result-handling)
    - [Cancellation handling](#cancellation-handling)
    - [Error handling](#error-handling)
      - [Error results](#error-results)
      - [Invalid configuration exceptions](#invalid-configuration-exceptions)
- [Events tracking](#events-tracking)
- [Custom event handler](#custom-event-handler)
- [Token expiry Handler](#token-expiry-handler)
- [NFC capture](#nfc-capture)
- [Going live](#going-live)
- [Additional info](#additional-info)

## Features

<img src="https://assets.complycube.com/images/complycube-android-sdk-github.jpg" alt="ComplyCube Android SDK illustrations"/>

**Native & intuitive UI**: We provide mobile-native screens that guide your customers in capturing their selfies, video recordings, government-issued IDs (such as passports, driving licenses, and residence permits), and proof of address documents (bank statements and utility bills)

**Liveness**: Our market-leading liveness detection provides accurate and extremely fast presence detection on your customers' selfies (3D Passive and Active) and documents to prevent fraud and protect your business. It detects and deters several spoofing vectors, including **printed photo attacks**, **printed mask attacks**, **video replay attacks**, and **3D mask attacks**.

**Auto-capture**: Our UI screens attempt to auto-capture your customer's documents and selfies and run quality checks to ensure that only legible captures are processed by our authentication service.

**Branding & customization**: You can customize the experience by adding your brand colors and your own text. Furthermore, screens can be added and removed.

**ComplyCube API**: Our [REST API](https://docs.complycube.com/api-reference) can be used to build entirely custom flows on top of this native mobile UI layer. We offer backend SDK libraries ([Node.js](https://www.npmjs.com/package/@complycube/api), [PHP](https://github.com/complycube/complycube-php), [Python](https://pypi.org/project/complycube/), and [.NET](https://www.nuget.org/packages/Complycube/)) to facilitate custom integrations.

**Localized**: We offer multiple localization options to fit your customer needs.

**Secure**: Our GPDR, CCPA, and ISO-certified platform ensure secure and data privacy-compliant end-to-end capture.

## Requirements

- Android 5.0 (API level 21) and above
- AndroidX
- Kotlin 1.5 and above

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

Then update your project level `build.gradle` file with the ComplyCube SDK repository maven settings:

```gradle
buildscript {
    ...
    repositories {
        ...
      
    }
    dependencies {
        ....
        //Check for the latest version here: http://plugins.gradle.org/plugin/com.jfrog.artifactory
        classpath "org.jfrog.buildinfo:build-info-extractor-gradle:4+"
    }
}

allprojects {
    apply plugin: "com.jfrog.artifactory"
    ...
}

artifactory {
  contextUrl = "${artifactory_contextUrl}"  
  resolve {
    repository {
      repoKey = 'cc-gradle-release-local'
      username = "${artifactory_user}"
      password = "${artifactory_password}"
      maven = true
    }
  }
}
```

Then update your module level `build.gradle` file with the SDK dependency:

```gradle
dependencies {
    implementation "com.complycube:sdk:+"
}

```

### 2. Creating a client

Before launching the SDK, your app must first [create a client](https://docs.complycube.com/api-reference/clients/create-a-client) using the ComplyCube API.

A client represents the individual on whom you need to perform identity verification checks on. A client is required to generate an SDK token.

This must be done on your **mobile app backend** server.

#### Example request

```bash
curl -X POST https://api.complycube.com/v1/clients \
     -H ' Authorization: <YOUR_API_KEY>' \
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

> You must generate a new token each time you initialize the ComplyCube Web SDK.

#### Example request

```bash
curl -X POST https://api.complycube.com/v1/tokens \
     -H ' Authorization: <YOUR_API_KEY>' \
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

### 4. Initialize an SDK flow

Now you can initialize a flow with the default settings of a Document, Selfie and Proof of Address capture with assistance enabled.

```kotlin
var clientAuth = ClientAuth("SDK_TOKEN", "CLIENT_ID")

var complycubeFlow = ComplyCubeSdk.Builder(this,
            callback = { result ->
                when (result) {
                    is Result.Success -> { /* Handle Success Result */ }
                    is Result.Canceled -> { /* Handle Cancelled Result */ }
                    is Result.Error -> { /* Handle Error Result */
                        when (result.errorCode) {
                            ComplyCubeErrorCode.UploadError -> { /* Handle Upload Error */ }
                            ComplyCubeErrorCode.BiometricStageCount -> { /* Handle BiometricStageCount Error */ }
                            ComplyCubeErrorCode.DocumentMandatory -> { /* Handle DocumentMandatory Error */ }
                            ComplyCubeErrorCode.ExpiredToken -> { /* Handle ExpiredToken Error */ }
                            ComplyCubeErrorCode.FlowError -> { /* Handle Flow Error */ }
                            ComplyCubeErrorCode.InvalidCountryCode -> { /* Handle InvalidCountryCode Error */ }
                            ComplyCubeErrorCode.JailBroken -> { /* Handle JailBroken Error */ }
                            ComplyCubeErrorCode.NoDocumentTypes -> { /* Handle NoDocumentTypes Error */ }
                            ComplyCubeErrorCode.NoResult -> { /* Handle NoResult Error */ }
                            ComplyCubeErrorCode.NotAuthorized -> { /* Handle NotAuthorized Error */ }
                            ComplyCubeErrorCode.Unknown -> { /* Handle Unknown Error */ }
                            ComplyCubeErrorCode.UnsupportedCountryTypeCombination -> { /* Handle UnsupportedCountryTypeCombination Error */ }
                            ComplyCubeErrorCode.Connectivity -> { /* Handle Connectivity Error */ }
                            ComplyCubeErrorCode.NoDiskAccess -> { /* Handle NoDiskAccess Error */ }
                            ComplyCubeErrorCode.NoUserConsent -> { /* Handle NoUserConsent Error */ }
                            ComplyCubeErrorCode.UnsupportedDocumentType -> { /* Handle UnsupportedDocumentType Error */ }
                        }
                    }
                    else -> { }
                }
            })
complycubeFlow.start(clientAuth)
```

### 5. Perform checks

Using the `StageResults` returned by the flow, you can trigger your **mobile backend** to run the necessary checks on your client.

For example, use the properties:

- `StageResult.Document.Id` to run a document check
- `StageResult.Document.Id` and `StageResult.LivePhoto.Id` to run an identity check
- `StageResult.Document.Id` and `StageResult.LiveVideo.Id` to run an enhanced identity check
- `StageResult.ProofOfAddress.Id` to run a proof of address check

#### Example request

```bash
curl -X POST https://api.complycube.com/v1/checks \
     -H ' Authorization: <YOUR_API_KEY>' \
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

### Stages

Each stage in the flow can be customized to create the ideal journey for your clients.

The snippet below demonstrates how you can set up a customized flow using the ComplyCube SDK

```kotlin
var complycubeFlow = ComplyCubeSdk.Builder(this, callback = ...)
                        .withSDKToken("SDK_Token")
                        .withClientId("CLIENT_ID")
                        .withStages(
                            Welcome(...),
                            Consent(...),
                            Document(...),
                            SelfiePhoto(...),
                            ProofOfAddress(...)
                            Complete(...)
                        )
                        .withLookAndFeel(...) 
                        .withCustomLanguage(...)
complycubeFlow.start()
```

#### Welcome stage

This is the first screen of the flow. It displays a welcome message and a summary of the stages you have configured for the client. If you would like to use a custom title and message, you can set them as follows:

``` kotlin
var welcomeStage = Welcome(
                       title = "Custom Screen Title",
                       message = "Custom welcome message" )
```

> The welcome stage will always default to show as the first screen.

#### Consent stage

You can optionally add this stage to enforce explicit consent collection before the client can progress in the flow. The consent screen allows you to set a custom title.

``` kotlin
var consentStage = Consent(
                       title = "Custom Consent Screen Title"
                   )
```

#### Document stage

This stage allows clients to select the type of identity document they would like to submit. You can customize these screens to:

- Limit the scope of document types the client can select, e.g., Passport only.
- Set the document issuing countries they are allowed for each document type.
- Show or hide the instruction screens before capture.
- Set a retry limit to allow clients to progress the journey regardless of capture quality.

> If you provide only one document type, the document type selection screen will be skipped. The country selection screen will be skipped if you provide only a single country for a given document type.

You can remove the information screens shown before camera captures by enabling or disabling guidance. You should only consider omitting this if you have clearly informed your customer of the capture steps required.

> :warning: Please note the `retryLimit` you set here will take precedence over the retry limit that has been set globally in the [Web Portal](https://portal.complycube.com/automations).

``` kotlin
var documentStage = Document (
                        /* Set document types and limit the enabled countries */
                        Passport(),DrivingLicence((Country.GB, Country.US)),

                        /* Enable or disable additional guidance for the user */
                        isGuidanceEnabled = true,

                        /* Enable or disable the ability to upload an image from file */
                        useLiveCaptureOnly = true,

                        /* Set the number of retry attempts before the image is 
                        uploaded without soft checks */
                        retryLimit = 3
                    )
```

#### Selfie photo and video stage

You can request a selfie photo ([live photo](https://docs.complycube.com/api-reference/live-photos)) capture or video ([live video](https://docs.complycube.com/api-reference/live-videos)) capture from your customer.

There are two types of Selfie stage that you can add to your Flow stages, a ```SelfiePhoto``` or ```SelfieVideo```

SelfiePhoto stage will take a picture of the customer and perform fast fail checks before confirming with the customer they are happy to submit.

``` kotlin
var selfiePhoto = SelfiePhoto(
                    /* Enable or disable a smart assistant or have the 
                    user manually capture the image */
                    isMLAssistantEnabled = false
                  )
```

or

SelfieVideo stage will take a video of the customer with an active challenge the customer has to complete.

``` kotlin
var selfieVideo = SelfieVideo(
                    /* Enable or disable a smart assistant or have the 
                    user manually capture the image */
                    isMLAssistantEnabled = false
                  )
```

> :warning: If you attempt to add both, the SDK will throw a `ComplyCubeSDKException` error stating `ConflictingStages`.

#### Proof of address stage

When requesting a proof of address document, you can set the allowed document type and whether the client can upload the document. When `useLiveCaptureOnly` is set to false, the client will be forced to perform a live capture.

```kotlin
var poaStage = ProofOfAddress(
                /* A list of supported document types that can be submitted */
                UtilityBill(),BankStatement(),
                
                /* Enable or disable the ability to upload an image from file */
                useLiveCaptureOnly = false,
                ...
               )
```

#### Completion stage

You can add an optional completion stage at the end of the process and let the customer know the process has been completed.

```kotlin
var completionStage = Complete(
                          title: "Thank you!",
                          message: "Your KYC submission has been completed, our onboarding team will come back to you shortly" )
```

### Look and feel

The SDK allows you to set colors to match your existing application or brand. You can customize the colors by setting the relevant values when building your flow.

```kotlin
complycubeFlow.withLookAndFeel(lookAndFeel = LookAndFeel (primaryButtonColor = Color.RED))
```

| Appearance property | Description |
| --- | ----------- |
| ```primaryButtonColor``` | Primary action button background color. |
| ```primaryButtonTextColor``` | Primary action button text color. |
| ```primaryButtonBorderColor``` | Primary action button border color. |
| ```secondaryButtonColor``` | Secondary button background color. |
| ```secondaryButtonTextColor``` | Secondary action button text color. |
| ```secondaryButtonBorderColor``` | Secondary action button border color. |
| ```documentSelectorColor``` | Document type selection button color. |
| ```documentSelectorBorderColor``` | Document type selection button border color. |
| ```documentSelectorIconColor``` | Document type icon color. |
| ```documentSelectorTitleTextColor``` | Document type title text color. |
| ```documentSelectorDescriptionTextColor``` | Document type description text color. |
| ```bodyTextColor``` | Screen body text color. |
| ```headingTextColor``` | Title heading text color. |
| ```subheadingTextColor``` | Subheading text color. |
| ```uiInterfaceStyle``` | Set the SDK to use dark mode (```.dark```),  light mode (```.light```), or system inherited (```.inherited```). |

### Localization

The SDK provides the following language support:

- Arabic - `ar` :united_arab_emirates:
- Dutch - `nl` :netherlands:
- English - `en` :uk:
- French - `fr` :fr:
- German - `de` :de:
- Hindi - `hi` :india:
- Italian - `it` :it:
- Norwegian - `no` :norway:
- Polish - `po` :poland:
- Portuguese - `pt` :portugal:
- Spanish - `es` :es:
- Swedish - `sv` :sweden:
- Chinese (Simplified) - `zh` :cn:

### Callback Handling

#### Result handling

When initializing your client flow, you will need to register a result handler to process the outcome of the flow.

```kotlin
var complycubeFlow = ComplyCubeSdk.Builder(this) {
    flowResult ->
    when(flowResult) {
        is Result.Error -> // Your callback code here
        is Result.Success -> // Your callback code here
        is Result.Canceled -> // Your callback code here
    }
}
```

When the outcome is a `Result.Success`, you can create [check requests](https://docs.complycube.com/api-reference/checks/create-a-check) using the captured data. The IDs of the uploaded resources are returned in the `stages` property.

For example, our default flow, which includes an Identity Document, Selfie (Live Photo), and Proof of Address, would have a stages collection that looks like this.

```kotlin
( // ID of Identity Document uploaded
  StageResult.Document.Id, 
  // ID of Live Photo uploaded as Selfie
  StageResult.LivePhoto.Id, 
  // ID of Proof of Address uploaded.
  StageResult.ProofOfAddress.Id)
```

#### Cancellation handling

If the client exits the SDK flow before completion, the description provided by `Result.Cancelled` will specify the reason.

It's possible that the client advanced as far as the upload stage before choosing to cancel. In such cases, some data may already have been uploaded to their record.

#### Error handling

##### Error results

If the SDK experiences any issues, the error callback will contain one of the following error codes

| Error | Description |
| --- | ----------- |
| ```ComplyCubeErrorCode.NotAuthorized``` | The SDK has attempted a request to an endpoint you are not authorized to use.|
| ```ComplyCubeErrorCode.ExpiredToken``` | The token used to initialize the SDK has expired. Create a new SDK token and restart the flow. |
| ```ComplyCubeErrorCode.DocumentMandatory``` | A **Document stage** is mandatory with the currently configured stages. |
| ```ComplyCubeErrorCode.JailBroken``` | The SDK cannot be launched on this device as it has been compromised. |
| ```ComplyCubeErrorCode.NoDocumentTypes``` | A **Document stage** has been initialized without setting document types. |
| ```ComplyCubeErrorCode.BiometricStageCount``` | The configuration provided contains duplicate **Selfie photo** or **Selfie video** stages. |
| ```ComplyCubeErrorCode.UploadError``` | An error occurred during the upload document or selfie upload process. |
| ```ComplyCubeErrorCode.InvalidCountryCode``` | An invalid country code is provided. |
| ```ComplyCubeErrorCode.UnsupportedCountryTypeCombination``` | An unsupported country code is provided for a specific document type. |
| ```ComplyCubeErrorCode.NoUserConsent``` | The user has not given consent to using the SDK. |
| ```ComplyCubeErrorCode.NoResult``` | No Result is given to the callback when returning back to your up. If this keeps occuring, let us know about it. |
| ```ComplyCubeErrorCode.Unknown``` | An unexpected error has occurred. If this keeps occurring, let us know about it. |
| ```ComplyCubeErrorCode.FlowError``` | An unrecoverable error occurred during the flow.|
| ```ComplyCubeErrorCode.Connectivity``` | A Network error has occured. |
| ```ComplyCubeErrorCode.NoDiskAccess``` | The user has declined disk access permission. |
| ```ComplyCubeErrorCode.UnsupportedDocumentType``` | An unsupported document is provided. |

##### Invalid configuration exceptions

If the SDK is misconfigured, attempting to launch the flow builder will trigger an exception. These exceptions can be caught and handled using a catch clause.

| Error | Description |
| --- | ----------- |
| ```ComplyCubeSDKException.MissingToken``` | Attempted to launch the SDK without setting the SDK token. |
| ```ComplyCubeSDKException.DuplicateStages``` | Launch configuration contains duplicate stages. |
| ```ComplyCubeSDKException.UploadRequireGuidance``` | If `useLiveCaptureOnly` is set to `false`, enabling the guidance feature is required. This can be done by setting `isGuidanceEnabled` to `true`.|
| ```ComplyCubeSDKException.Unknown``` | An unexpected error has occurred. If this keeps occurring, let us know about it. |

## Events tracking

Below is the list of events being tracked by the SDK:

| Event | Description |
| --- | --- |
| ```BIOMETRICS_STAGE_SELFIE_CAMERA``` | The client reached capture camera for a selfie. |
| ```BIOMETRICS_STAGE_SELFIE_CAMERA_MANUAL_MODE``` | The client reached manual capture camera for a selfie. |
| ```BIOMETRICS_STAGE_SELFIE_CAPTURE_GUIDANCE``` | The client has reached the guidance screen showing how to take a good selfie. |
| ```BIOMETRICS_STAGE_SELFIE_CHECK_QUALITY``` | The client has reached the photo review screen after capturing a selfie photo.. |
| ```BIOMETRICS_STAGE_VIDEO_ACTION_ONE``` | The client reached the first action in a video selfie |
| ```BIOMETRICS_STAGE_VIDEO_ACTION_TWO``` | The client reached the second action in a video selfie. |
| ```BIOMETRICS_STAGE_VIDEO_CAMERA``` | The client reached capture camera for a video selfie. |
| ```BIOMETRICS_STAGE_VIDEO_CAMERA_MANUAL_MODE``` | The client reached manual capture camera for a video selfie. |
| ```BIOMETRICS_STAGE_VIDEO_CHECK_QUALITY``` | The client has reached the video review screen after recording a video selfie. |
| ```CAMERA_ACCESS_PERMISSION``` | The client has reached the permission request screen for camera permissions. |
| ```COMPLETION_STAGE``` | The client has reached the Completion screen. |
| ```CONSENT_STAGE``` | The client has reacher the consent stage screen. |
| ```CONSENT_STAGE_WARNING``` | The client has attempted to exit without giving consent and receive a confirmation prompt. |
| ```DOCUMENT_STAGE_TWO_SIDE_CHECK_QUALITY_BACK``` | The client reached quality preview screen for the back side of a two-sided ID document. |
| ```DOCUMENT_STAGE_TWO_SIDE_CHECK_QUALITY_FRONT``` | The client reached quality preview screen for the front side of a two-sided ID document. |
| ```DOCUMENT_STAGE_ONE_SIDE_CHECK_QUALITY``` | The client reached image quality preview screen for one-sided ID document. |
| ```DOCUMENT_STAGE_TWO_SIDE_CAMERA_BACK``` | The client reached camera for the back side of a two-sided ID document. |
| ```DOCUMENT_STAGE_TWO_SIDE_CAMERA_BACK_MANUAL_MODE``` | The client reached manual capture camera for the back side of two-sided ID document. |
| ```DOCUMENT_STAGE_TWO_SIDE_CAMERA_FRONT``` | The client reached camera stage for the front side of two-sided ID document. |
| ```DOCUMENT_STAGE_TWO_SIDE_CAMERA_FRONT_MANUAL_MODE``` | The client reached manual capture camera for the back side of two-sided ID document. |
| ```DOCUMENT_STAGE_ONE_SIDE_CAMERA_MANUAL_MODE``` | The client reached manual capture camera of one-sided ID document. |
| ```DOCUMENT_STAGE_ONE_SIDE_CAMERA``` | The client reached the capture camera stage for a one-sided ID document. |
| ```DOCUMENT_STAGE_DOCUMENT_TYPE``` | The client has reached the document type selection screen for an ID Document capture stage. |
| ```DOCUMENT_STAGE_SELECT_COUNTRY``` | The client reached country selection screen for ID document. |
| ```DOCUMENT_STAGE_CAPTURE_GUIDANCE``` | The client reached capture guidance screen for ID document. |
| ```INTRO``` | The client has reached the intro screen. |
| ```PROOF_OF_ADDRESS_STAGE_TWO_SIDE_CHECK_QUALITY_FRONT``` | The client reached quality preview screen for the front side of a two-sided proof of address document. |
| ```PROOF_OF_ADDRESS_STAGE_CAPTURE_GUIDANCE``` | The client has reach capture guidance screen for proof of address document. |
| ```PROOF_OF_ADDRESS_STAGE_TWO_SIDE_CHECK_QUALITY_BACK``` | The client reached quality preview screen for the back side of a two-sided proof of address document. |
| ```PROOF_OF_ADDRESS_STAGE_ONE_SIDE_CHECK_QUALITY``` | The client reached quality preview screen for a one-sided proof of address document. |
| ```PROOF_OF_ADDRESS_STAGE_DOCUMENT_TYPE``` | The client has reached the document type selection screen for a Proof Of Address capture stage. |
| ```PROOF_OF_ADDRESS_STAGE_ONE_SIDE_CAMERA``` | The client reached capture camera stage for a one-sided proof of address. |
| ```PROOF_OF_ADDRESS_STAGE_TWO_SIDE_CAMERA_FRONT_MANUAL_MODE``` | The client reached manual capture camera for the front side of a two-sided proof address document. |
| ```PROOF_OF_ADDRESS_STAGE_TWO_SIDE_CAMERA_FRONT``` | The client reached capture camera for the front side of a two-sided proof address document. |
| ```PROOF_OF_ADDRESS_STAGE_TWO_SIDE_CAMERA_BACK_MANUAL_MODE``` | The client reached manual capture camera for the back side of a two-sided proof address document. |
| ```PROOF_OF_ADDRESS_STAGE_ONE_SIDE_CAMERA_MANUAL_MODE``` | The client reached manual capture camera for the front side of a one-sided proof address document. |
| ```PROOF_OF_ADDRESS_STAGE_SELECT_COUNTRY``` | The client reached country selection screen for a proof of address document. |
| ```PROOF_OF_ADDRESS_STAGE_TWO_SIDE_CAMERA_BACK``` | The client reached camera for the back side of a two-sided proof address document. |

## Custom event handler

If you want to implement your own user tracking, the SDK enables you to insert your custom tracking code for the [tracked events](#events-tracking).

To incorporate your own tracking, define a function and apply it using `withEventHandler` when initializing the `Builder`:

```swift
let sdk = ComplyCubeMobileSDK.Builder()
          .withEventHandler(handler: ComplyCubeCustomEventHandler)
```

## Token expiry Handler

If you want to automatically manage token expiration, you can use a callback function to generate a new token and seamlessly continue the process with it.

```kotlin
let sdk = ComplyCubeMobileSDK.Builder()
            .withTokenExpiryHandler({ () -> String in
              // Insert custom token renewal code here
            })
```

## NFC capture

With the ComplyCube SDK, you can read NFC-enabled identity documents and confirm their authenticity and identity.

To perform an NFC read, you'll first have to scan the document to obtain the necessary key for accessing the chip.

> :information_source: Please get in touch with your **Account Manager** or **[support](https://support.complycube.com/hc/en-gb/requests/new)** to get access to our NFC enabled Mobile SDK.

The SDK supports the following features

- Basic access control
- Secure messaging
- Passive Authentication
- Active authentication
- Chip authentication

The **NFC stage** can only be initialized following a **Document stage**, otherwise you will encounter a `ComplyCubeErrorCode.DocumentMandatory` error.

``` kotlin
var complycubeFlow = ComplyCubeSdk.Builder(this, callback = ...)
                        .withStages(
                            Welcome(...),
                            Consent(...),
                            Document(...),
 			    NFC(...),
                            SelfiePhoto(...),
                            ProofOfAddress(...),
                            Complete(...)
                        )
                        .withLookAndFeel(...)
                        .withCustomLanguage(...)
 
```

## Going live

Check out our handy [integration checklist here](https://docs.complycube.com/documentation/guides/integration-checklist) before you go live.

## Additional info

You can find our full [API reference here](https://docs.complycube.com/api-reference), and our guides and example flows can be found [here](https://docs.complycube.com/documentation/).
