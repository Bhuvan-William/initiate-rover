#ifdef  _WIN64
#pragma warning (disable:4996)
#endif

#include <cstdio>
#include <cassert>
#include <stdlib.h>
#include <string.h>

#if defined(WIN32)
# include <conio.h>
#else
# include "conio.h"
#endif

#include <HD/hd.h>
#include <HDU/hduVector.h>
#include <HDU/hduError.h>

HDCallbackCode HDCALLBACK DevicePositionCallback(void *pUserData);
void PrintDevicePosition();

bool down;
bool pdown;
bool rdown;
hduVector3Dd f;

HDCallbackCode HDCALLBACK FrictionlessPlaneCallback(void *data)
{
    const double planeStiffness = 1;

    hdBeginFrame(hdGetCurrentDevice());

    hduVector3Dd position;
    hdGetDoublev(HD_CURRENT_POSITION, position);

	if (position[1] < 0) 
	{
		double toppen = fabs(position[1]);
		f[1] = toppen*planeStiffness;
	}
	else if (position[1] > 0)
	{
		double toppen = fabs(position[1]);
		f[1] = toppen*planeStiffness*-1;	
	}

	if (position[2] < 0)
	{
		double toppen = fabs(position[2]) - 0;
	    f[2] = toppen*planeStiffness;
	}
	else if (position[2] > 75)
	{
		double toppen = fabs(position[2]) - 75;
	    f[2] = -1 * toppen*planeStiffness;
	}

	if (position[0] < -90)
	{
		double toppen = fabs(position[0]) - 90;
	    f[0] = toppen*planeStiffness;
	}
	else if (position[0] > 90)
	{
		double toppen = fabs(position[0]) - 90;
	    f[0] = -1 * toppen*planeStiffness;
	}


	hdSetDoublev(HD_CURRENT_FORCE, f);
    hdEndFrame(hdGetCurrentDevice());

    HDErrorInfo error;
    if (HD_DEVICE_ERROR(error = hdGetError()))
    {
        hduPrintError(stderr, &error, "Error detected during main scheduler callback\n");

        if (hduIsSchedulerError(&error))
        {
            return HD_CALLBACK_DONE;  
        }
    }

    return HD_CALLBACK_CONTINUE;
}


int main(int argc, char* argv[])
{
    HDErrorInfo error;
    HHD hHD = hdInitDevice("Touch me");

    hdEnable(HD_FORCE_OUTPUT);
    hdStartScheduler();

    HDCallbackCode hPlaneCallback = hdScheduleAsynchronous(
        FrictionlessPlaneCallback, 0, HD_DEFAULT_SCHEDULER_PRIORITY);


    while (HD_TRUE)
    {       
        PrintDevicePosition();
    }

    hdStopScheduler();
    hdUnschedule(hPlaneCallback);
    hdDisableDevice(hHD);

    return 0;
}


HDCallbackCode HDCALLBACK DevicePositionCallback(void *pUserData)
{
    HDdouble *pPosition = (HDdouble *) pUserData;

    //hdBeginFrame(hdGetCurrentDevice());
    hdGetDoublev(HD_CURRENT_POSITION, pPosition);
    //hdEndFrame(hdGetCurrentDevice());

    return HD_CALLBACK_DONE;
}


void PrintDevicePosition()
{
    hduVector3Dd position;

    hdScheduleSynchronous(DevicePositionCallback, position,
        HD_DEFAULT_SCHEDULER_PRIORITY);

    HDint nCurrentButtons;
    hdGetIntegerv(HD_CURRENT_BUTTONS, &nCurrentButtons);

	float a = (position[0] + 90)*1920 / 180 + 0;
	float b = (position[2] + 0)*1080 / 75 + 0;

	if (a > 1920)
	{
		a = 1920;
	}
	if (a < 0) 
	{
		a = 0;
	}
	if (b > 1080) 
	{
		b = 1080;
	}
	if (b < 0) 
	{
		b = 0;
	}

	char buffer[50];
	sprintf(buffer, "xdotool mousemove %.1f %.1f", a, b);
	
	if (position[1] < -15 && pdown == false) {
		system("xdotool mousedown 1");
		pdown = true;
	}
	else {
		if ((nCurrentButtons & HD_DEVICE_BUTTON_1) != 0 && down == false && pdown==false)
    	{
			system("xdotool mousedown 1");
			down = true;
    	}	
		else if ((nCurrentButtons & HD_DEVICE_BUTTON_1) == 0 && pdown == false)
		{
			system("xdotool mouseup 1");
			down = false;	
		}
		else if (pdown == true && position[1] > -13)
		{
			system("xdotool mouseup 1");
			pdown = false;
		}	
	}

	if ((nCurrentButtons & HD_DEVICE_BUTTON_2) != 0 && rdown == false)
    {
		system("xdotool click 3");
		rdown = true;
    }
	if ((nCurrentButtons & HD_DEVICE_BUTTON_2) == 0)
	{
		rdown = false;
	}

   	system(buffer);

	FILE *f = fopen("/home/robot/Documents/yeet.txt", "w");

	fprintf(f, "x%.3f:y%.3f:z%.3f:", 
		    position[0], position[1], position[2]);

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

	fclose(f);
}
