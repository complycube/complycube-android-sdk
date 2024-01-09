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
    ): View? {
        //Initialize flow
        complycubeFlow = ComplyCubeSdk.Builder(this,::flowResultHandler).apply {
            withCustomColors(customColors = SdkColors( primaryButtonColor = Color.RED.toLong()))
        }
        _binding = FragmentFirstBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.buttonFirst.setOnClickListener {
            complycubeFlow?.start(
                ClientAuth(
                    token = "SDK TOKEN",
                    clientId = "CLIENT ID"
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