package com.complycube.complycubesampleapp

import android.os.Bundle
import com.google.android.material.snackbar.Snackbar
import androidx.appcompat.app.AppCompatActivity
import androidx.navigation.findNavController
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.navigateUp
import androidx.navigation.ui.setupActionBarWithNavController
import android.view.Menu
import android.view.MenuItem
import androidx.activity.ComponentActivity
import com.complycube.complycubesampleapp.databinding.ActivityMainBinding
import com.complycube.sdk.ComplyCubeSdk
import com.complycube.sdk.common.data.ClientAuth
import com.complycube.sdk.common.data.IdentityDocumentType
import com.complycube.sdk.common.data.Stage

class MainActivity : AppCompatActivity() {

    private lateinit var appBarConfiguration: AppBarConfiguration
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        var builder = ComplyCubeSdk.Builder(this){

        }
        // Prepare stages
        val documentStage = Stage.CustomStage.Document(
            IdentityDocumentType.Passport(),
            IdentityDocumentType.ResidencePermit()
        )
        builder.withStages(Stage.DefaultStage.Welcome(), documentStage)
        builder.start(
            ClientAuth(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjoiWm1Rd01tTXhNekl3WldWbU9XSTFOamszWVdOaU1XTXdZV0ZsTVdVek1UVm1ORFF3TldJeE5EVXhPV0U1TkRBM1pEWXdZVGcxT1dRd016RmlZakUwTVRkak56WTBabVUxTVRaa05tRXpaVFF3TUdFM09EWTBZalEyWmpJMk4yWm1aR0k0TW1aa04yWXlOVEk0WW1SbE1XTmhOMkppWmpZeE1tSXdZemhtWTJGaVlqQTNPR1JpTXpGaFpEQmlOREF6TVRNNU16WmxNREF3T0RVM1pXUTVaamxtWkRNM056ZGxaRFkyTUdKalpqSTVaR1kzTlRNd09UY3pOVGRrWm1OaVlqaGxaRFUyWWpSaFl6YzVaalk1TW1VM1ltSTRZelZsTlRBMk5qRXpaalZsTjJWaU1qTTNaVEl3WldRelpXUTVNalpsTldGaFpXWmhZamt5T1RJek5RPT0iLCJ1cmxzIjp7ImFwaSI6Imh0dHBzOi8vYXBpLmNvbXBseWN1YmUuY29tIiwic3luYyI6IndzczovL3hkcy5jb21wbHljdWJlLmNvbSIsImNyb3NzRGV2aWNlIjoiaHR0cHM6Ly94ZC5jb21wbHljdWJlLmNvbSJ9LCJvcHRpb25zIjp7ImhpZGVDb21wbHlDdWJlTG9nbyI6ZmFsc2UsImVuYWJsZUN1c3RvbUxvZ28iOnRydWUsImVuYWJsZVRleHRCcmFuZCI6dHJ1ZSwiZW5hYmxlQ3VzdG9tQ2FsbGJhY2tzIjp0cnVlfSwiaWF0IjoxNjY3NDgzODUzLCJleHAiOjE2Njc0ODc0NTN9.8qnAcJ_t3-_6-JKIzj3q56TE8lJuQOReNBTAYfAvkss"
            ,"6363c8cc808c610008278c30"
        )
        )
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.toolbar)

        val navController = findNavController(R.id.nav_host_fragment_content_main)
        appBarConfiguration = AppBarConfiguration(navController.graph)
        setupActionBarWithNavController(navController, appBarConfiguration)

        binding.fab.setOnClickListener { view ->
            Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
                .setAction("Action", null).show()
        }
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        // Inflate the menu; this adds items to the action bar if it is present.
        menuInflater.inflate(R.menu.menu_main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        return when (item.itemId) {
            R.id.action_settings -> true
            else -> super.onOptionsItemSelected(item)
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        val navController = findNavController(R.id.nav_host_fragment_content_main)
        return navController.navigateUp(appBarConfiguration)
                || super.onSupportNavigateUp()
    }
}