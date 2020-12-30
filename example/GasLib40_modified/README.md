# Modified GasLib40 Instance

This gas network simulation problem was derived from the original GasLib-40
(see [GasLib40](#GasLib40), [GasLib40](#GasLib40) and [Pfetsch et al.](#Pfetsch)
Test data set whose original sources can be found (as of december the 29th of 2020) at

        http://gaslib.zib.de

among other gas network data sets. If your markdown renderer fails to link the 3 
provided references properly: see _References_ at the end of this README.md file. 

Important changes/modifications are (but not limited to):
 * this instance is a (independently developed) transient gas 
   network scenario whereas the original is a stationary one
 * an intersection node has been removed and replaced by a 'gas network 
   station' consisting of additional pipes, nodes, more compressor 
   stations, and a control valve allowing more complex operation modes
   
## Notes and Informations on Licenses

As of december the 29th of 2020:  
The original GasLib-40 instance had been licensed under the 
[Creative Commons Attribution 3.0 Unported License](http://creativecommons.org/licenses/by/3.0/)
It is part of the BMWi project 0328006 "Technical Capacities of Gas Networks".

This _modified GasLib40_ version however is licensed
by the same license as all of this git repository (including the 
__gas network simulator__, __cycADa__ and __paso__) of which it is part of.

Please note that this 'license information' about the _modified GasLib40_ 
is merely an informal reference to the actual License information 
(see LICENSE at the very top of this repo).

## References

 * <a name="GasLib40">[GasLib40]</a> Martin Schmidt, Denis Aßmann, 
   Robert Burlacu, Jesco Humpola, Imke Joormann, 
   Nikolaos Kanelakis, Thorsten Koch, Djamal Oucherif, 
   Marc E. Pfetsch, Lars Schewe, Robert Schwarz & Mathias Sirvent (2017)
   GasLib - A Library of Gas Network Instances,
   Data 2, No. 4, article 40
 * <a name="GasLib">[GasLib]</a> Martin Schmidt, Denis Aßmann, 
   Robert Burlacu, Jesco Humpola, Imke Joormann, 
   Nikolaos Kanelakis, Thorsten Koch, Djamal Oucherif, 
   Marc E. Pfetsch, Lars Schewe, Robert Schwarz & Mathias Sirvent (continuously updated)
   GasLib - A Library of Gas Network Instances,
   Report at Optimization Online 
   (see http://www.optimization-online.org/DB_HTML/2015/11/5216.html)
 * <a name="Pfetsch">[Pfetsch et al.]</a> Pfetsch et al. (2012) 
   Validation of Nominations in Gas Network Optimization:
   Models, Methods, and Solutions, ZIB-Report 12-41
