# ComplyCube Android SDK Sample Application

## Pre requisites
* AndroidX
* API level 21 (Android 5.0) and above
* Kotlin 1.5+

## Overview 
The ComplyCube SDK provides the tools necessary for Android developers to easily embed the data capture processes you need for identity verification. Our smart capture screens guide end users to ensure the best possible quality of identity documents, selfies and video recordings.

You can also customise the experience by adding/removing screens, customising colours and setting your own titles and text.

## 1. Installing the SDK

Start by adding your access credentials for the ComplyCube SDK repository to the gradle.properties file.

```gradle
artifactory_user= "USERNAME"
artifactory_password= "ENCRYPTED PASS"
artifactory_contextUrl= https://complycuberepo.jfrog.io/artifactory
```

Then update your application build.gradle file with the ComplyCube SDK repository maven settings and SDK dependency

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

## 2. Creating a Client

Before you can launch the SDK your app will need to [create a Client](https://docs.complycube.com/api-reference/clients/create-a-client) using the ComplyCube API. This must be done on your application server.

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

## 3. Creating a SDK Token

Once you have created a Client the new Client ID will need to be used to create an SDK token by using the [Generate a token endpoint](https://docs.complycube.com/api-reference/other-resources/tokens/generate-a-token).

```bash
curl -X POST https://api.complycube.com/v1/tokens \
     -H 'Authorization: <YOUR_API_KEY>' \
     -H 'Content-Type: application/json' \
     -d '{
          	"clientId":"CLIENT_ID",
          	"appId": "com.complycube.sampleapp"
        }'
```

The token is used to automatically upload the clients data to their client record. Therefore it is critical to generate a token each time the client could potentially change in your application.

## 4. Initialize a flow with default settings

To get started you can intialize a flow with the default settings. This will enable all guidance screens and allow all possible identity document options.

```kotlin
var complycubeFlow = ComplyCubeSdk.Builder(this, callback= ...)
                        .withSDKToken("SDK_Token")
complycubeFlow.start()
```

## 5. Execute checks against your client
Using the StageResults returned by the flow, you can trigger your backend to run the necessary checks on your client. 

*For example, use the properties;*
* StageResult.Document.Id to run a document check
* StageResult.Document.Id and StageResult.LivePhoto.Id to run an identity check

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

## Customisation

### Customising Stages

Each stage in the flow can be customised to create the ideal journey for your customers.

##### Welcome stage customisation

The welcome stage will default to show as the first screen even if you try to place it further along the flow. This screen allow you to set a custom title and informative message to let your customer know about the KYC/identity verification process in more detail.

``` kotlin
var welcomeStage = Welcome( title = "Custom Screen Title", message = "Custom welcome message")
```

##### Consent stage

You can optionally include the consent stage to enforce explicit consent collection before the customer can progress in the flow. The consent screen allows you to set a custom title.

``` kotlin
var consentStage = Consent( title = "Custom Consent Screen Title")
```

##### Document stage customisation
This stage allows a user to select the type of identity document they would like to submit.
You can customise these screens to help your customers make only valid choices.
* Limit the document types the customer can select e.g. Passports only.
* Set the document issuing countries they are allowed for each document type.
* Add/remove automated capture using smart assistance.
* Show/hide the instruction screens before capture.
* Set a retry limit, to allow customers to progress the journey regardless of capture quality.

**_NOTE:_** If you provide only one document type, the document type selection screen will be skipped. If you provide only a single country for a given document type the country selection screen will be skipped.

By enabling/disabling guidance you can remove the information screen shown before camera capture. This should only be ommitted if you have clearly informed your customer of the capture steps required.

:warning: Please note the retryLimit you set here will take precedence over the retry limit that has been set globally in the [developer console](https://portal.complycube.com/automations/documentChecks).

``` kotlin
var documentStage = Document (
            Passport(),DrivingLicence((GB)), 
            isGuidanceEnabled = true,
            retryLimit = 3
        )
```

If you would like to set the countries across all document types (apart from passports as these all have the same format). You can set the top level country lists at the flow level.

```kotlin
var complycubeFlow = ComplyCubeSdk.Builder(this, callback= ...)
                        .withCountries(Country.GB, Country.US)
                        ....
```

##### Selfie Photo & Video Stage customisation
You can request a selfie photo capture or selfie video capture from your customer. 

``` kotlin
var selfiePhoto = SelfiePhoto(isGuidanceEnabled = true, isMLAssistantEnabled = false)
// or
var selfieVideo = SelfieVideo(isGuidanceEnabled = true, isMLAssistantEnabled = false)
```

:warning: If you attempt to add both the SDK will throw a ComplyCubeSDKException error stating ConflictingStages.

##### Proof of Address customisation
When requesting a proof of address you can set the allowed document type but also set if the user is allowed to upload from their device.

```kotlin
var poaStage = ProofOfAddress(UtilityBill(),BankStatement(), 
            useLiveCaptureOnly = false, 
            ...
        )
```
### Customising appearence

The SDK also allows colour customisations to match your existing application. You can customise the SDK colours by setting colour values when building your flow. 

```kotlin
complycubeFlow.withCustomColors(customColors = SdkColors( primaryButtonColor = Color.RED))
```
| Appearence property | Description |
| --- | ----------- |
| ```primaryButtonColor``` | Secondary action button background colour |
| ```primaryButtonTextColor``` | Primary action button text colour |
| ```primaryButtonBorderColor``` | Primary action button border colour |
| ```secondaryButtonColor``` | Secondar button background colour |
| ```secondaryButtonTextColor``` | Secondary action button text colour |
| ```secondaryButtonBorderColor``` | Secondary action button border colour |
| ```documentSelectorColor``` | Document type selection button colour |
| ```documentSelectorBorderColor``` | Document type selection button border colour|
| ```documentSelectorIconColor``` | Document type icon colour |
| ```documentSelectorTitleTextColor``` | Document type title text colour|
| ```documentSelectorDescriptionTextColor``` | Document type description text colour|
| ```bodyTextColor``` | Screen body text colour|
| ```headingTextColor``` | Title heading text colour |
| ```subheadingTextColor``` | Subheading text colour e.g. |

### Result handling
When initializing your client flow you will need to register a result handler to process the outcome of the flow.

```kotlin
var complycubeFlow = ComplyCubeSdk.Builder(this) { flowResult ->
            when(flowResult){
                is ComplyCubeResult.Error -> // Your callback code here
                is ComplyCubeResult.Success -> // Your callback code here
                is ComplyCubeResult.Canceled -> // Your callback code here
            }
        }
```

When the outcome is a Result.Success you can start making [check requests](https://docs.complycube.com/api-reference/checks/create-a-check) to validates the customers captured data. The ID's of the uploaded data is returned in the ```stages``` property

For example a default flow (Identity Document, Selfie and Proof of Address) would have a stages collection that looks like this.

```kotlin
    (StageResult.Document.Id, StageResult.LivePhoto.Id, StageResult.ProofOfAddress.Id)
```

### Error handling

#### Runtime errors
If the SDK experiences any issues the error callback will be triggered with a detailed exception.

| Error | Description |
| --- | ----------- |
| ```ComplyCubeResult.Error.NotAuthorised``` | The SDK has attempted a request to an endpoint you are not authorised to used please check with your account manager.|
| ```ComplyCubeResult.Error.TokenExpired``` | The token used to mount the SDK has expired please repeat the token request process and restart the flow. |
| ```ComplyCubeResult.Error.Unknown``` | Something unexpected has happened, let us know how this happened. |

#### Invalid configuration exceptions 
If the SDK is misconfigured the flow builder will raise an exception when attempting to launch.

| Error | Description |
| --- | ----------- |
| ```ComplyCubeSDKException.MissingToken``` | Attempted to launch the SDK without setting the Token |
| ```ComplyCubeSDKException.DuplicateStages``` | Launch configuration contains duplicate stages. |
| ```ComplyCubeSDKException.ConflictingStages``` | Biometric configuration contains both a Live Video and Live Photo stage|
| ```ComplyCubeSDKException.InvalidDeviceSetup``` | User device has been flagged as jailbroken |
| ```ComplyCubeSDKException.StageSettingConflict``` | If useLiveCaptureOnly is false guidance must be enabled |
| ```ComplyCubeSDKException.Unknown``` | Something unexpected has happened, let us know how this happened. |

### Localisation

The SDK provides the following language support

Chinese (Simplified) - zh :cn:
English - en :uk:
French - fr :fr:
German - de :de:
Italian - it :it:
Spanish - es :es:

### Going Live

ComplyCube uses webhooks to notify your application when an event happens in your account. Before you go live ensure you have setup the necessary webhooks to process your check results. [Check out the Webhooks guide here for more information.](https://docs.complycube.com/documentation/guides/webhooks)

Check out our handy [integration checklist here](https://docs.complycube.com/documentation/guides/integration-checklist) before you go-live.

### Additional Info

You can find our full [API reference here](https://docs.complycube.com/api-reference) and our guides and example flows can be found [here](https://docs.complycube.com/documentation/).