package com.complycube.complycubesampleapp

import android.graphics.Color
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import com.complycube.complycubesampleapp.databinding.FragmentFirstBinding
import com.complycube.sdk.ComplyCubeSdk
import com.complycube.sdk.common.data.ClientAuth
import com.complycube.sdk.common.data.CustomerInfoDetail
import com.complycube.sdk.common.data.CustomerInfoField
import com.complycube.sdk.common.data.CustomerInfoPersonField
import com.complycube.sdk.common.data.Result
import com.complycube.sdk.common.data.Stage.CustomStage.AddressCapture
import com.complycube.sdk.common.data.Stage.CustomStage.CustomerInfo
import com.complycube.sdk.common.data.Stage.CustomStage.Document
import com.complycube.sdk.common.data.Stage.CustomStage.ProofOfAddress
import com.complycube.sdk.common.data.Stage.CustomStage.SelfiePhoto
import com.complycube.sdk.common.data.Stage.DefaultStage.Complete
import com.complycube.sdk.common.data.Stage.DefaultStage.Welcome
import com.complycube.sdk.data.remote.model.response.ComponentFormat
import com.complycube.sdk.data.remote.model.response.ComponentType
import com.complycube.sdk.data.remote.model.response.Constraint
import com.complycube.sdk.data.remote.model.response.QuestionItemComponentFormat
import com.complycube.sdk.data.remote.model.response.QuestionOptionsItem
import com.complycube.sdk.presentation.theme.LookAndFeel
import com.complycube.sdk.presentation.theme.SdkColors

/**
 * A simple [Fragment] subclass as the default destination in the navigation.
 */
class FirstFragment : Fragment() {

    private var _binding: FragmentFirstBinding? = null

    // This property is only valid between onCreateView and
    // onDestroyView.
    private val binding get() = _binding!!
    private var complycubeFlow: ComplyCubeSdk.Builder? = null

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        //Initialize flow
        complycubeFlow = ComplyCubeSdk.Builder(this,::flowResultHandler)
        complycubeFlow?.withStages(
            Welcome(),
            Document(),
            SelfiePhoto(),
            AddressCapture(useAutoComplete = true),
            ProofOfAddress(),
//            CustomerInfo(
//                title = "CustomerInfo",
//                customerInfoFields = listOf(
//                        CustomerInfoField.Email,
//                        CustomerInfoField.Mobile,
//                        CustomerInfoField.JoinedDate,
//                        CustomerInfoField.Telephone,
//                        CustomerInfoField.ExternalId,
//                    CustomerInfoField.Details(
////                            CustomerInfoDetail.Company(
////                                listOf(
////                                    CustomerInfoCompanyField.NAME,
////                                    CustomerInfoCompanyField.WEBSITE,
////                                    CustomerInfoCompanyField.REGISTRATION_NUMBER,
////                                    CustomerInfoCompanyField.INCORPORATION_TYPE,
////                                    CustomerInfoCompanyField.INCORPORATION_COUNTRY,
////
////                                )
////                            ),
////
//                        CustomerInfoDetail.Person(
//                            listOf(
//                                    CustomerInfoPersonField.FIRST_NAME,
//                                    CustomerInfoPersonField.MIDDLE_NAME,
//                                    CustomerInfoPersonField.LAST_NAME,
//                                    CustomerInfoPersonField.GENDER,
//                                    CustomerInfoPersonField.DATE_OF_BIRTH,
//                                    CustomerInfoPersonField.BIRTH_COUNTRY,
//                                    CustomerInfoPersonField.NATIONALITY,
//                                    CustomerInfoPersonField.NATIONAL_IDENTITY_NUMBER,
//                                    CustomerInfoPersonField.SOCIAL_INSURANCE_NUMBER.copy(constraint = Constraint("metadata.jurisdiction contains US")),
//                                    CustomerInfoPersonField.SSN.copy(constraint = Constraint("metadata.has_ssn contains yes")),
//                                    CustomerInfoPersonField.TAX_IDENTIFICATION_NUMBER,
//                            )
//                        )
//                    ),
//                ),
//            ),
            Complete()
        )
//        complycubeFlow?.withWorkflowId("6762ec40bbbd950008d39e47")
        complycubeFlow?.withLookAndFeel(LookAndFeel(enableAnimations = true))
        _binding = FragmentFirstBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.buttonFirst.setOnClickListener {
            complycubeFlow?.start(
                ClientAuth(
                    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjoiTTJGa056VTNZamMzWTJKa1lqVTBZelUzTVRFd1pEZzVOV1UxTkdNNE0yWXlaVEZsWXpVMk1XWXhNalkwWWpFek1tTmlOalU0TlRnMU5HRXhOVGs0WWprMlpXWXdOV015TkRBNU1EZzBOR0poWWpaaU5EQXdOVGs0T0dNNE1XTTJOek5sWWpJNU1XUXlZamd3TlRZMk5qTTBOREJrTm1KaVpUSTFOekkxTnpGa05XUTRNamt3TVRabE5EUmpabVk0WVdWbE5UWm1Nell5TlRabU5qRmpNVGRsTVdJMU9UaGlNekkyT1RjeVl6VmxaRGsxTkdZeE9XVTNZakkxWmpZM1pUaGtPV0UxWVRnellqTTNNekl6TjJJNU5UbGxZakJrTnpBeE5EYzRaRE5tWXpFNFkySTVPR0l4T0RCak1HVTROVGMzTXpnNVpHVXlNalk0WXpZeE16WTVPVGRpTlRsak16VTRPRGhrWm1Vek5qaGxPVGM0WldNME5UUTRNVGsxIiwidXJscyI6eyJhcGkiOiJodHRwczovL2FwaS5jb21wbHljdWJlLmNvbSIsInN5bmMiOiJ3c3M6Ly94ZHMuY29tcGx5Y3ViZS5jb20iLCJjcm9zc0RldmljZSI6Imh0dHBzOi8veGQuY29tcGx5Y3ViZS5jb20ifSwib3B0aW9ucyI6eyJoaWRlQ29tcGx5Q3ViZUxvZ28iOmZhbHNlLCJlbmFibGVDdXN0b21Mb2dvIjp0cnVlLCJlbmFibGVUZXh0QnJhbmQiOnRydWUsImVuYWJsZUN1c3RvbUNhbGxiYWNrcyI6dHJ1ZSwiZW5hYmxlTmZjIjp0cnVlLCJpZGVudGl0eUNoZWNrTGl2ZW5lc3NBdHRlbXB0cyI6NSwiZG9jdW1lbnRJbmZsaWdodFRlc3RBdHRlbXB0cyI6MiwibmZjUmVhZEF0dGVtcHRzIjo1LCJlbmFibGVBZGRyZXNzQXV0b2NvbXBsZXRlIjp0cnVlLCJlbmFibGVXaGl0ZUxhYmVsaW5nIjpmYWxzZX0sImlhdCI6MTc2MjI0MTcyOCwiZXhwIjoxNzYyMjQ1MzI4fQ.r1-Ar3bHbpt944p795I8qwZqIQ9LM6PKSTSs5dtpnk4",
                    clientId = "6875fb819b4d200002899140"
                )
            )
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    private fun flowResultHandler(flowResult: Result?) {
        when(flowResult){
            is Result.Error -> {
                Log.i("CC-RESULT-ERROR", flowResult.toString())
            }
            is Result.Success -> {
                Log.i("CC-RESULT-SUCCESS", flowResult.toString())
            }
            is Result.Canceled -> {
                Log.i("CC-RESULT-CANCELLED", flowResult.toString())
            }
            else -> {
                Log.i("CC-RESULT-ERROR", flowResult.toString())
            }
        }
    }
}