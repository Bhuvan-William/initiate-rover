/*****************************************************************************

Copyright (c) 2004 SensAble Technologies, Inc. All rights reserved.

OpenHaptics(TM) toolkit. The material embodied in this software and use of
this software is subject to the terms and conditions of the clickthrough
Development License Agreement.

For questions, comments or bug reports, go to forums at: 
    http://dsc.sensable.com

Module Name:

  FrictionlessPlane.cpp

Description: 

  This example demonstrates how to haptically render contact with an infinite
  frictionless plane.  The plane allows popthrough such that if the user 
  applies enough force against the plane, the plane will reverse its sidedness
  and allow the user to interact with it from the opposite side.

*******************************************************************************/
#ifdef  _WIN64
#pragma warning (disable:4996)
#endif

#include <cstdio>
#include <cassert>
#include <time.h>
#include <unistd.h>

#if defined(WIN32)
# include <conio.h>
#else
# include "conio.h"
#endif

#include <HD/hd.h>
#include <HDU/hduVector.h>
#include <HDU/hduError.h>

#define BUZZ_SIZE 1024

HDCallbackCode HDCALLBACK DevicePositionCallback(void *pUserData);
void PrintDevicePosition();
void Jolt();


/*******************************************************************************
 Haptic plane callback.  The plane is oriented along Y=0 and provides a 
 repelling force if the device attempts to penetrates through it.
*******************************************************************************/
HDCallbackCode HDCALLBACK FrictionlessPlaneCallback(void *data)
{
    

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
		
		char str[80];
		int i;

		char buff[BUZZ_SIZE];
		FILE *f = fopen("/home/robot/Documents/yeet.txt", "r");
		fgets(buff, BUZZ_SIZE, f);
		fclose(f);

		if (buff[0] == 'J')
		{
			Jolt();
			f = fopen("/home/robot/Documents/yeet.txt", "w");

			const char *text = "f";
			fprintf(f, "%s", text);
		
			fclose(f);
		}


    }

    hdStopScheduler();
    hdUnschedule(hPlaneCallback);
    hdDisableDevice(hHD);

    return 0;
}


HDCallbackCode HDCALLBACK DevicePositionCallback(void *pUserData)
{
    HDdouble *pPosition = (HDdouble *) pUserData;

   	hdBeginFrame(hdGetCurrentDevice());
    hdGetDoublev(HD_CURRENT_POSITION, pPosition);
   	hdEndFrame(hdGetCurrentDevice());

    return HD_CALLBACK_DONE;
}


void PrintDevicePosition()
{
    hduVector3Dd position;

    hdScheduleSynchronous(DevicePositionCallback, position,
        HD_DEFAULT_SCHEDULER_PRIORITY);


    HDint nCurrentButtons;
    hdGetIntegerv(HD_CURRENT_BUTTONS, &nCurrentButtons);

	

	FILE *f = fopen("/home/robot/Documents/pos.txt", "w");
	
	//fprintf(f, "%f\n", position[0]);
    //fprintf(f, "x%.3f:y%.3f:z%.3f:", 
    //    position[0], position[1], position[2]);
	fprintf(f, "hmm");


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


    fprintf(f, "\n");
	fclose(f);
}

//Delivers a small jolt of haptic feedback to the arm
void Jolt()
{		
		hduVector3Dd f;

		hdBeginFrame(hdGetCurrentDevice());
		f.set(0, 100, 0);
		hdSetDoublev(HD_CURRENT_FORCE, f);
    	hdEndFrame(hdGetCurrentDevice());

		usleep(50000);

		hdBeginFrame(hdGetCurrentDevice());
		f.set(0, 0, 0);
		hdSetDoublev(HD_CURRENT_FORCE, f);
  		hdEndFrame(hdGetCurrentDevice());
}




