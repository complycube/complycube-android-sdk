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
                    token = "..YOUR_TOKEN",
                    clientId = "YOUR_CLIENT_ID"
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