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
import com.complycube.sdk.common.data.Result
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
        complycubeFlow?.withLookAndFeel(LookAndFeel(enableAnimations = true))
        _binding = FragmentFirstBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.buttonFirst.setOnClickListener {
            complycubeFlow?.start(
                ClientAuth(
                    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjoiTTJGa056VTNZamMzWTJKa1lqVTBZelUzTVRFd1pEZzVOV1UxTkdNNE0yWXlaVEZsWXpVMk1XWXhNalkwWWpFek1tTmlOalU0TlRnMU5HRXhOVGs0WWpGak9XTm1PR05rTlRWak9XUTBPVEEyWldNeU9UWTRPV1kzTURZelpEWXpZemRqT0RCbE56azFOVFUwWVRoak1Ea3pNMlV5WTJWaFkyUTVNVEUxTldFek1USTRNV1V3WVRFNU9EY3pPREk1TXpkaU4yVmhZemRqWW1Jd05UZGtZalJrTWpkaU5UVmpaRGczWkdZMVlUVmxOV1E0TnpBMFpUQTFaakZtTWprek1tUXpaR0UxWldZek1EUTNOR1psWkRKak1qUXhNR1JpTXprMFpEUTBPR0ZqWkRZME16Sm1OemhrT0RFM1pETTRZbVF3TW1SaFpqWTFNVFZqT1RNeVpBPT0iLCJ1cmxzIjp7ImFwaSI6Imh0dHBzOi8vYXBpLmNvbXBseWN1YmUuY29tIiwic3luYyI6IndzczovL3hkcy5jb21wbHljdWJlLmNvbSIsImNyb3NzRGV2aWNlIjoiaHR0cHM6Ly94ZC5jb21wbHljdWJlLmNvbSJ9LCJvcHRpb25zIjp7ImhpZGVDb21wbHlDdWJlTG9nbyI6ZmFsc2UsImVuYWJsZUN1c3RvbUxvZ28iOnRydWUsImVuYWJsZVRleHRCcmFuZCI6dHJ1ZSwiZW5hYmxlQ3VzdG9tQ2FsbGJhY2tzIjp0cnVlLCJlbmFibGVOZmMiOmZhbHNlLCJpZGVudGl0eUNoZWNrTGl2ZW5lc3NBdHRlbXB0cyI6NSwiZG9jdW1lbnRJbmZsaWdodFRlc3RBdHRlbXB0cyI6MiwibmZjUmVhZEF0dGVtcHRzIjo1LCJlbmFibGVBZGRyZXNzQXV0b2NvbXBsZXRlIjp0cnVlLCJlbmFibGVXaGl0ZUxhYmVsaW5nIjp0cnVlfSwiaWF0IjoxNzI3MTc0NjU3LCJleHAiOjE3MjcxNzgyNTd9.nNVmg4HL4v6hAoa1GDvOe0Exdaa1dZykqfa63olzi9E",
                    clientId = "66f27dd9f63537000824e92c"
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