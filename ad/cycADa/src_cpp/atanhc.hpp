/*
 * makeshift implementation of atanhc: x*atanhc(x) = atanh(x), with atanh the inverse hyperbolic tangent
 *
 * __author__ = ('Tom Streubel', 'Christian Strohm') # alphabetical order of surnames
 * __credits__ = ('Andreas Griewank', 'Richard Hasenfelder',
 *                'Oliver Kunst', 'Lutz Lehmann',
 *                'Manuel Radons', 'Philpp Trunschke') # alphabetical order of surnames
 */


#include <boost/math/special_functions/atanh.hpp>

namespace boost{
	namespace math{
		double atanhc(double x){
			if(x != 0.0){
				return atanh(x)/x;
			}else{
				return 1.0;
			}
		}
	}
}

//int main(){
//
//	double x = 0.5;
//
//	std::cout << "Hello atanhc World" << std::endl;
//
//	std::cout << "atanhc(" << x << ") = " << boost::math::atanhc(x) << std::endl;
//
//	for(int i=0; i < 100; i++){
//		x /= 2.0;
//
//		std::cout << "atanhc(" << x << ") = " << boost::math::atanhc(x) << std::endl;
//	}
//
//	x = 0.0;
//
//	std::cout << "atanhc(" << x << ") = " << boost::math::atanhc(x) << std::endl;
//
//	return 0;
//}


































































































