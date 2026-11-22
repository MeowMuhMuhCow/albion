#include <bbdef.h>
#include <bbdsa.h>
#include <bbevent.h>
#include <bbsystem.h>
#include <bbbasmem.h>

#include <string.h>
void BLEV_Check_keyboard(void); void BLEV_Init_keyboard(void);
#include "include\blvintrn.h"
#include "..\..\lib\asminc\BB_INL_A.H"

#ifdef BBBLEV_ERRORHANDLING
	#include <BBERROR.h>
	#include <stdio.h>
#endif

/* Die folgende Konstante definiert die Größe des Eventbuffers */
#define BLEV_MAXEVENTS	32

/* BLEV Library status */
BOOLEAN BLEV_Library_Status = FALSE;

/* Das folgende Array enthält den Ringbuffer */
BLEV_Event_struct a_events[ BLEV_MAXEVENTS];

/* Die folgenden Variablen legen Anfang und Ende des belegten Bereiches im Ringbuffer fest. */

/* Enthält den Index des Elementes im Ringbuffer, das als nächstes ausgelesen werden muß, oder
    anders gesagt, den Event, der als nächstes zurückgeliefert wird */
SILONG	sl_next_get_event;

/* Enthält den Index des Elementes im Ringbuffer, an das als nächstes ein Eintrag geschrieben
   wird. */
SILONG	sl_next_put_event;

/* Error handling */
#ifdef BBBLEV_ERRORHANDLING

	/* Name of Library */
	char BBBLEV_LibraryName[] = "BBEVENT Library";

#endif


/* Dieses Flag gibt Auskunft über den Status des Ringbuffers. */
enum { BLEV_BUFFER_EMPTY, BLEV_EVENT_IN_BUFFER, BLEV_BUFFER_FULL } en_bufferstatus;

/*
 ******************************************************************************
 * #FUNCTION HEADER BEGIN#
 * NAME     : BLEV_Init
 * FUNCTION : Initialize the event library (event buffer, mouse and keyboard).
 * FILE     : D:\PCLIB32\SRC\BBEVENT\BBEVENT.C
 * AUTHOR   : Rainer Reber
 * FIRST    : 13.06.95 00:16:56
 * LAST     : 13.06.95 00:16:56
 * INPUTS   :  void  : 
 * RESULT   : SILONG : 
 * BUGS     : 
 * NOTES    :	Achtung !!! Wenn BLEV_Init aufgerufen wurde sollte davor auf jeden
 *							Fall auch DSA_Init und SYSTEM_Init aufgerufen worden sein
 *						wird ansonsten auch automatisch erledigt
 * VERSION  : 1.0 
 * #FUNCTION HEADER END#
 */

/* #FUNCTION BEGIN# */

SILONG BLEV_Init( void )
{
	/* DSALibrary wird ben”tigt welche BASEMEM initialisiert */
	if(!DSA_Init()){
		#ifdef BBBLEV_ERRORHANDLING
		{
			/* Local vars */
			struct BBBLEV_ErrorStruct error;

			/* Fill out error structure */
			error.errorname	= "BLEV_Init: Cannot Init DSA";
			error.errordata	= 0;

			/* Push error on stack */
			ERROR_PushError( BLEV_PrintError, ( UNCHAR * ) &BBBLEV_LibraryName[0], sizeof( struct BBBLEV_ErrorStruct ), ( UNBYTE * ) &error );
		}
		#endif
		return(FALSE);
	}

	/* Library already initialised ? */
	if( BLEV_Library_Status ){
		/* Yes: nothing to do */
		return(TRUE);
	}

	/* Der Buffer wird als leer gekennzeichnet und die beiden Indexvariablen entsprechend gesetzt */
	en_bufferstatus	= BLEV_BUFFER_EMPTY;
	sl_next_get_event = 0;
	sl_next_put_event = 0;

	BLEV_Init_keyboard();

	BLEV_Library_Status=TRUE;

	return( TRUE );
}

/* #FUNCTION END# */



/*
 ******************************************************************************
 * #FUNCTION HEADER BEGIN#
 * NAME     : BLEV_Exit
 * FUNCTION : Exit the event library.
 * FILE     : D:\PCLIB32\SRC\BBEVENT\BBEVENT.C
 * AUTHOR   : Rainer Reber
 * FIRST    : 13.06.95 00:16:28
 * LAST     : 13.06.95 00:16:28
 * INPUTS   :  void  : 
 * RESULT   : None.
 * BUGS     : 
 * NOTES    : 
 * VERSION  : 1.0 
 * #FUNCTION HEADER END#
 */

/* #FUNCTION BEGIN# */

void BLEV_Exit( void )
{
	/* Library already initialised ? */
	if( !BLEV_Library_Status ){
		/* Yes: nothing to do */
		return;
	}

	/* Hier ist momentan nix zu tun.. */
	BLEV_Library_Status=FALSE;

}

/* #FUNCTION END# */

/*
 ******************************************************************************
 * #FUNCTION HEADER BEGIN#
 * NAME     : BLEV_IsEventWaiting
 * FUNCTION : Warten bis Event auftritt
 * FILE     : D:\PCLIB32\SRC\BBEVENT\BBEVENT.C
 * AUTHOR   : Rainer Reber
 * FIRST    : 13.06.95 00:15:59
 * LAST     : 13.06.95 00:15:59
 * INPUTS   :  void  : 
 * RESULT   : SILONG : 
 * BUGS     : 
 * NOTES    : 
 * VERSION  : 1.0 
 * #FUNCTION HEADER END#
 */

/* #FUNCTION BEGIN# */

SILONG BLEV_IsEventWaiting( void )
{
	return( en_bufferstatus != BLEV_BUFFER_EMPTY );
}

/* #FUNCTION END# */

/*
 ******************************************************************************
 * #FUNCTION HEADER BEGIN#
 * NAME     : BLEV_ClearAllEvents
 * FUNCTION : Event Stack entleeren
 * FILE     : D:\PCLIB32\SRC\BBEVENT\BBEVENT.C
 * AUTHOR   : Rainer Reber
 * FIRST    : 13.06.95 00:14:25
 * LAST     : 13.06.95 00:14:25
 * INPUTS   :  
 * RESULT   : None.
 * BUGS     : 
 * NOTES    : 
 * VERSION  : 1.0 
 * #FUNCTION HEADER END#
 */

/* #FUNCTION BEGIN# */

void BLEV_ClearAllEvents( void )
{
	/* Der Buffer wird als leer gekennzeichnet und die beiden Indexvariablen entsprechend gesetzt */
	en_bufferstatus	= BLEV_BUFFER_EMPTY;
	sl_next_get_event = 0;
	sl_next_put_event = 0;
}

/* #FUNCTION END# */

/*
 ******************************************************************************
 * #FUNCTION HEADER BEGIN#
 * NAME     : BLEV_PutEvent
 * FUNCTION : Event auf Eventstack kopieren
 * FILE     : D:\PCLIB32\SRC\BBEVENT\BBEVENT.C
 * AUTHOR   : Rainer Reber
 * FIRST    : 13.06.95 00:13:15
 * LAST     : 13.06.95 00:13:15
 * INPUTS   :  struct BLEV_Event_struct		*p_event  : Zeiger auf zu erzeugenden Event
 * RESULT   : SILONG : TRUE = Event konnte erzeugt werden
 *										 FALSE = Event Buffer voll
 * BUGS     : 
 * NOTES    : 
 * VERSION  : 1.0 
 * #FUNCTION HEADER END#
 */

/* #FUNCTION BEGIN# */

#pragma off (check_stack)

SILONG BLEV_PutEvent( struct BLEV_Event_struct		*p_event )
{

	/* Wenn der Buffer voll ist, gibt's einen Fehler */
	if(  en_bufferstatus == BLEV_BUFFER_FULL )
	{
		return( FALSE );
	};

	/* Der Event wird in den Buffer kopiert */
//	memcpy( &a_events[ sl_next_put_event ], p_event, sizeof( BLEV_Event_struct ));
	intmemcopy( (UNBYTE *)p_event, (UNBYTE *)&a_events[ sl_next_put_event ], sizeof( BLEV_Event_struct ) );

	/* Anpassen des Endezeigers. Dabei eventuell den Wraparound berücksichtigen */
	if( (++sl_next_put_event) == BLEV_MAXEVENTS )
		/* Wraparound */
		sl_next_put_event = 0;

	/* Testen, ob durch das Einfügen der Buffer voll wurde */
	if( sl_next_put_event == sl_next_get_event )
		en_bufferstatus = BLEV_BUFFER_FULL;
	else
		en_bufferstatus = BLEV_EVENT_IN_BUFFER;

	return( TRUE );

}

#pragma on (check_stack)

/* #FUNCTION END# */




/*
 ******************************************************************************
 * #FUNCTION HEADER BEGIN#
 * NAME     : BLEV_GetEvent
 * FUNCTION : Event vom EventStack holen
 * FILE     : D:\PCLIB32\SRC\BBEVENT\BBEVENT.C
 * AUTHOR   : Rainer Reber
 * FIRST    : 13.06.95 00:11:40
 * LAST     : 13.06.95 00:11:40
 * INPUTS   :  struct BLEV_Event_struct	*p_event  : Zeiger auf Event-Struktur
 * RESULT   : SILONG : TRUE = Event wurde bergeben
 *										 FALSE = keine Event mehr im Buffer
 * BUGS     : 
 * NOTES    : 
 * VERSION  : 1.0 
 * #FUNCTION HEADER END#
 */

/* #FUNCTION BEGIN# */

SILONG BLEV_GetEvent( struct BLEV_Event_struct	*p_event )
{
	BLEV_Check_keyboard();
	/* Testen, ob der Buffer leer ist, oder ob er ein gültiges Element enthält */
	if(  en_bufferstatus == BLEV_BUFFER_EMPTY )
	{
		/* wenn kein Event erzeugt Mausposition trotzdem zurckgeben */
		p_event->sl_eventtype 	= BLEV_NOEVENT;
		p_event->p_screenport 	= SYSTEM_ActiveScreenPort;
		p_event->ul_pressed_keys	= SYSTEM_GetBLEVStatusLong();
		p_event->sl_key_code		= 0;
		p_event->sl_mouse_x		= SYSTEMVAR_mousex;
		p_event->sl_mouse_y		= SYSTEMVAR_mousey;

		return( FALSE );
	};

	/* Kopieren des Events in den Parameter */
//	memcpy( p_event, &a_events[ sl_next_get_event ], sizeof( BLEV_Event_struct ));
	intmemcopy( (UNBYTE *)&a_events[ sl_next_get_event ],(UNBYTE *)p_event, sizeof( BLEV_Event_struct ));

	/* Der Zeiger auf das nächste zu lesende Element wird weitergeschaltet */
	/* Anpassen des Endezeigers. Dabei eventuell den Wraparound berücksichtigen */
	if( (++sl_next_get_event) == BLEV_MAXEVENTS )
		/* Wraparound */
		sl_next_get_event = 0;

	/* Testen, ob durch das Entnehmen der Buffer leer wurde */
	if( sl_next_get_event == sl_next_put_event )
		en_bufferstatus = BLEV_BUFFER_EMPTY;
	else
		en_bufferstatus = BLEV_EVENT_IN_BUFFER;

	return( TRUE );

}
/* #FUNCTION END# */



/*
******************************************************************************
* #FUNCTION HEADER BEGIN#
* NAME      : BLEV_GetMouseX
* FUNCTION  : Mausposition X auslesen
* INPUTS    :
* RESULT    :
* FILE      :
* AUTHOR    :
* FIRST     :
* LAST      :
* BUGS      :
* NOTES     :
* SEE ALSO  :
* VERSION   : 0.1
* #FUNCTION HEADER END#
*/

/* #FUNCTION BEGIN# */
void BLEV_GetMousePos(struct BBPOINT *pnt)
{
	pnt->x=SYSTEMVAR_mousex;
	pnt->y=SYSTEMVAR_mousey;
}

/*
 ******************************************************************************
 * #FUNCTION HEADER BEGIN#
 * NAME      : BLEV_PrintError
 * FUNCTION  : Print error function for BLEV library
 * INPUTS    : UNCHAR * buffer	:Pointer to string buffer.
 *             UNBYTE * data	:Pointer to error stack data area.
 * RESULT    : None.
 * #FUNCTION HEADER END#
 */

/* #FUNCTION BEGIN# */

#ifdef BBBLEV_ERRORHANDLING

	void
	BLEV_PrintError( UNCHAR * buffer, UNBYTE * data )
	{
		/* Local vars */
		struct BBBLEV_ErrorStruct * BLEVErrorStructPtr=( struct BBBLEV_ErrorStruct * ) data;

		/* sprintf error message into string buffer */
		sprintf( ( char * ) buffer, "ERROR! %s %ld ", ( char * ) BLEVErrorStructPtr->errorname, BLEVErrorStructPtr->errordata );
	}

#endif

/* #FUNCTION END# */

/* Keyboard input through the BIOS (in the original at the end of this module, 0x88b83) */

#include <bios.h>

UNSHORT BLEV_Key_table[128];
/*
 ******************************************************************************
 * #FUNCTION HEADER BEGIN#
 * NAME      : BLEV_Check_keyboard
 * FUNCTION  : Read pending keys through the BIOS and turn them into events.
 * FILE      : BBEVENT.C
 * AUTHOR    : - (no original header; written for the reconstruction)
 * INPUTS    : None.
 * RESULT    : None.
 * #FUNCTION HEADER END#
 */

void
BLEV_Check_keyboard(void)
{
	struct BLEV_Event_struct Event;
	UNSHORT Key;
	UNSHORT Ascii;
	UNSHORT Scan;

	if (!(SYSTEM_Init_Flags & SYSTEM_FLAG_NOKEYINT))
	{
		Key = _bios_keybrd(_NKEYBRD_READY);
		while (Key)
		{
			Ascii = Key & 0x00FF;
			Scan = ((UNSHORT)(Key & 0x7F00)) >> 8;

			_bios_keybrd(_NKEYBRD_READ);

			Event.sl_eventtype		= BLEV_KEYDOWN;
			Event.p_screenport		= SYSTEM_ActiveScreenPort;
			Event.ul_pressed_keys	= SYSTEM_GetBLEVStatusLong();
			Event.sl_mouse_x			= SYSTEMVAR_mousex;
			Event.sl_mouse_y			= SYSTEMVAR_mousey;

			switch (Ascii)
			{
				case 0:
				case 0xE0:
					if (BLEV_Key_table[Scan])
						Event.sl_key_code = BLEV_Key_table[Scan];
					else
						Event.sl_key_code = Ascii;
					break;
				case 8:
					Event.sl_key_code = BLEV_BS;
					break;
				case 9:
					Event.sl_key_code = BLEV_TAB;
					break;
				case 13:
					Event.sl_key_code = BLEV_RETURN;
					break;
				case 27:
					Event.sl_key_code = BLEV_ESC;
					break;
				default:
					Event.sl_key_code = Ascii;
					break;
			}

			BLEV_PutEvent(&Event);

			Key = _bios_keybrd(_NKEYBRD_READY);
		}
	}
}
/*
 ******************************************************************************
 * #FUNCTION HEADER BEGIN#
 * NAME      : BLEV_Init_keyboard
 * FUNCTION  : Fill the scan code table for the BIOS keyboard.
 * FILE      : BBEVENT.C
 * AUTHOR    : - (no original header; written for the reconstruction)
 * INPUTS    : None.
 * RESULT    : None.
 * #FUNCTION HEADER END#
 */

void
BLEV_Init_keyboard(void)
{
	UNSHORT i;

	for (i = 0; i < 128; i++)
		BLEV_Key_table[i] = 0;

	BLEV_Key_table[59] = BLEV_F1;
	BLEV_Key_table[60] = BLEV_F2;
	BLEV_Key_table[61] = BLEV_F3;
	BLEV_Key_table[62] = BLEV_F4;
	BLEV_Key_table[63] = BLEV_F5;
	BLEV_Key_table[64] = BLEV_F6;
	BLEV_Key_table[65] = BLEV_F7;
	BLEV_Key_table[66] = BLEV_F8;
	BLEV_Key_table[67] = BLEV_F9;
	BLEV_Key_table[68] = BLEV_F10;
	BLEV_Key_table[5]  = BLEV_F11;
	BLEV_Key_table[6]  = BLEV_F12;
	BLEV_Key_table[82] = BLEV_INS;
	BLEV_Key_table[83] = BLEV_DEL;
	BLEV_Key_table[71] = BLEV_HOME;
	BLEV_Key_table[79] = BLEV_END;
	BLEV_Key_table[73] = BLEV_PGUP;
	BLEV_Key_table[81] = BLEV_PGDN;
	BLEV_Key_table[75] = BLEV_LEFT;
	BLEV_Key_table[72] = BLEV_UP;
	BLEV_Key_table[77] = BLEV_RIGHT;
	BLEV_Key_table[80] = BLEV_DOWN;

	BLEV_Key_table[104] = BLEV_F1;
	BLEV_Key_table[105] = BLEV_F2;
	BLEV_Key_table[106] = BLEV_F3;
	BLEV_Key_table[107] = BLEV_F4;
	BLEV_Key_table[108] = BLEV_F5;
	BLEV_Key_table[109] = BLEV_F6;
	BLEV_Key_table[110] = BLEV_F7;
	BLEV_Key_table[111] = BLEV_F8;
	BLEV_Key_table[112] = BLEV_F9;
	BLEV_Key_table[113] = BLEV_F10;
	BLEV_Key_table[11]  = BLEV_F11;
	BLEV_Key_table[12]  = BLEV_F12;
	BLEV_Key_table[34]  = BLEV_INS;
	BLEV_Key_table[35]  = BLEV_DEL;
	BLEV_Key_table[23]  = BLEV_HOME;
	BLEV_Key_table[31]  = BLEV_END;
	BLEV_Key_table[25]  = BLEV_PGUP;
	BLEV_Key_table[33]  = BLEV_PGDN;
	BLEV_Key_table[27]  = BLEV_LEFT;
	BLEV_Key_table[29]  = BLEV_UP;
	BLEV_Key_table[24]  = BLEV_RIGHT;
	BLEV_Key_table[32]  = BLEV_DOWN;

	BLEV_Key_table[94]  = BLEV_F1;
	BLEV_Key_table[95]  = BLEV_F2;
	BLEV_Key_table[96]  = BLEV_F3;
	BLEV_Key_table[97]  = BLEV_F4;
	BLEV_Key_table[98]  = BLEV_F5;
	BLEV_Key_table[99]  = BLEV_F6;
	BLEV_Key_table[100] = BLEV_F7;
	BLEV_Key_table[101] = BLEV_F8;
	BLEV_Key_table[102] = BLEV_F9;
	BLEV_Key_table[103] = BLEV_F10;
	BLEV_Key_table[9]   = BLEV_F11;
	BLEV_Key_table[10]  = BLEV_F12;
	BLEV_Key_table[20]  = BLEV_TAB;
	BLEV_Key_table[18]  = BLEV_INS;
	BLEV_Key_table[19]  = BLEV_DEL;
	BLEV_Key_table[119] = BLEV_HOME;
	BLEV_Key_table[117] = BLEV_END;
	BLEV_Key_table[4]   = BLEV_PGUP;
	BLEV_Key_table[118] = BLEV_PGDN;
	BLEV_Key_table[115] = BLEV_LEFT;
	BLEV_Key_table[116] = BLEV_UP;
	BLEV_Key_table[13]  = BLEV_RIGHT;
	BLEV_Key_table[17]  = BLEV_DOWN;

	BLEV_Key_table[84] = BLEV_F1;
	BLEV_Key_table[85] = BLEV_F2;
	BLEV_Key_table[86] = BLEV_F3;
	BLEV_Key_table[87] = BLEV_F4;
	BLEV_Key_table[88] = BLEV_F5;
	BLEV_Key_table[89] = BLEV_F6;
	BLEV_Key_table[90] = BLEV_F7;
	BLEV_Key_table[91] = BLEV_F8;
	BLEV_Key_table[92] = BLEV_F9;
	BLEV_Key_table[93] = BLEV_F10;
	BLEV_Key_table[7]  = BLEV_F11;
	BLEV_Key_table[8]  = BLEV_F12;
}
