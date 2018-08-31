/*

	Continously writes the coordinates and button states of the geomagic touch to a file

*/
#ifdef  _WIN64
#pragma warning (disable:4996)
#endif

#include <stdio.h>
#include <assert.h>

#if defined(WIN32)
# include <windows.h>
#else
# include <unistd.h>
# define Sleep(x) usleep((x) * 1000)
#endif

#include <HD/hd.h>
#include <HDU/hduError.h>
#include <HDU/hduVector.h>

HDCallbackCode HDCALLBACK UpdateCalibrationCallback(void *pUserData);
HDCallbackCode HDCALLBACK CalibrationStatusCallback(void *pUserData);
HDCallbackCode HDCALLBACK DevicePositionCallback(void *pUserData);

HDenum GetCalibrationStatus();
HDboolean CheckCalibration(HDenum calibrationStyle);
void PrintDevicePosition();



int main(int argc, char* argv[])
{
    HHD hHD;
    HDErrorInfo error;
    int supportedCalibrationStyles;
    int calibrationStyle;
    
    hHD = hdInitDevice("Touch me");
    if (HD_DEVICE_ERROR(error = hdGetError())) 
    {
        hduPrintError(stderr, &error, "Failed to initialize haptic device");
        fprintf(stderr, "\nPress any key to quit.\n");
        getch();
        return -1;
    }

    hdGetIntegerv(HD_CALIBRATION_STYLE, &supportedCalibrationStyles);
    if (supportedCalibrationStyles & HD_CALIBRATION_ENCODER_RESET)
    {
        calibrationStyle = HD_CALIBRATION_ENCODER_RESET;
    }
    if (supportedCalibrationStyles & HD_CALIBRATION_INKWELL)
    {
        calibrationStyle = HD_CALIBRATION_INKWELL;
    }
    if (supportedCalibrationStyles & HD_CALIBRATION_AUTO)
    {
        calibrationStyle = HD_CALIBRATION_AUTO;
    }

    hdStartScheduler();
    if (HD_DEVICE_ERROR(error = hdGetError()))
    {
        hduPrintError(stderr, &error, "Failed to start the scheduler");
        return -1;           
    }



    while (!_kbhit())
    {
        if (CheckCalibration(calibrationStyle))
        {
            PrintDevicePosition();
        }
    }
    
    hdStopScheduler();
    hdDisableDevice(hHD);

    return 0;
}


HDCallbackCode HDCALLBACK UpdateCalibrationCallback(void *pUserData)
{
    HDenum *calibrationStyle = (int *) pUserData;

    if (hdCheckCalibration() == HD_CALIBRATION_NEEDS_UPDATE)
    {
        hdUpdateCalibration(*calibrationStyle);
    }

    return HD_CALLBACK_DONE;
}

HDCallbackCode HDCALLBACK CalibrationStatusCallback(void *pUserData)
{
    HDenum *pStatus = (HDenum *) pUserData;

    hdBeginFrame(hdGetCurrentDevice());
    *pStatus = hdCheckCalibration();
    hdEndFrame(hdGetCurrentDevice());

    return HD_CALLBACK_DONE;
}

HDCallbackCode HDCALLBACK DevicePositionCallback(void *pUserData)
{
    HDdouble *pPosition = (HDdouble *) pUserData;

    hdBeginFrame(hdGetCurrentDevice());
    hdGetDoublev(HD_CURRENT_POSITION, pPosition);
    hdEndFrame(hdGetCurrentDevice());

    return HD_CALLBACK_DONE;
}

HDenum GetCalibrationStatus()
{
    HDenum status;
    hdScheduleSynchronous(CalibrationStatusCallback, &status,
                          HD_DEFAULT_SCHEDULER_PRIORITY);
    return status;
}

HDboolean CheckCalibration(HDenum calibrationStyle)
{
    HDenum status = GetCalibrationStatus();
    
    if (status == HD_CALIBRATION_OK)
    {
        return HD_TRUE;
    }
    else if (status == HD_CALIBRATION_NEEDS_MANUAL_INPUT)
    {

        return HD_FALSE;
    }
    else if (status == HD_CALIBRATION_NEEDS_UPDATE)
    {
        hdScheduleSynchronous(UpdateCalibrationCallback, &calibrationStyle,
            HD_DEFAULT_SCHEDULER_PRIORITY);

        if (HD_DEVICE_ERROR(hdGetError()))
        {

            return HD_FALSE;
        }
        else
        {

            return HD_TRUE;
        }
    }
    else
    {
        assert(!"Unknown calibration status");
        return HD_FALSE;
    }
}

void PrintDevicePosition()
{
	//gets the position
    hduVector3Dd position;
    hdScheduleSynchronous(DevicePositionCallback, position,
        HD_DEFAULT_SCHEDULER_PRIORITY);


	//gets the current buttons
    HDint nCurrentButtons;
    hdGetIntegerv(HD_CURRENT_BUTTONS, &nCurrentButtons);

	FILE *f = fopen("/home/robot/Documents/pos.txt", "w");
	
	//writes the position of the arm to a file
    fprintf(f, "x%.3f:y%.3f:z%.3f:", position[0], position[1], position[2]);

	//writes the button states to the file
    if ((nCurrentButtons & HD_DEVICE_BUTTON_1) != 0)
    {
	fprintf(f, "1:");
    }
    else if ((nCurrentButtons & HD_DEVICE_BUTTON_1) == 0)
    {
        fprintf(f, "0:");
    }
    if ((nCurrentButtons & HD_DEVICE_BUTTON_2) != 0)
    {
		fprintf(f, "1");
    }
    else if ((nCurrentButtons & HD_DEVICE_BUTTON_2) == 0)
    {
        fprintf(f, "0");
    }

	//safely closes the file after finishing the line
    fprintf(f, "\n");
	fclose(f);
}
