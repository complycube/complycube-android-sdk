package com.complycube.complycubesampleapp

import android.graphics.Color
import android.os.Bundle
import android.util.Log
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import com.complycube.complycubesampleapp.databinding.FragmentFirstBinding
import com.complycube.sdk.ComplyCubeSdk
import com.complycube.sdk.common.data.IdentityDocumentType
import com.complycube.sdk.common.data.ComplyCubeResult
import com.complycube.sdk.common.data.Stage.CustomStage.*
import com.complycube.sdk.common.data.Stage.DefaultStage.*
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
        var a = ComplyCubeSdk.Builder(this,::flowResultHandler)
            .withCustomColors(customColors = SdkColors( primaryButtonColor = Color.RED)))
        _binding = FragmentFirstBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.buttonFirst.setOnClickListener {
            complycubeFlow?.start()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    private fun flowResultHandler(flowResult: ComplyCubeFlowResult?) {
        when(flowResult){
            is ComplyCubeFlowResult.Error -> {
                Log.i("CC-RESULT-ERROR", flowResult.toString())
            }
            is ComplyCubeFlowResult.Success -> {
                Log.i("CC-RESULT-SUCCESS", flowResult.toString())
            }
            is ComplyCubeFlowResult.Canceled -> {
                Log.i("CC-RESULT-CANCELLED", flowResult.toString())
            }
            else -> {
                Log.i("CC-RESULT-ERROR", flowResult.toString())
            }
        }
    }
}